"""
CardioAI - Fase 05: Assistente Conversacional & IA Generativa
Desafio Ir Além 1: Integração Real com API de LLM (OpenAI 'gpt-4o-mini' / Gemini)

Este módulo substitui a simulação local por uma integração real com LLMs de produção:
1. Extração estruturada de sintomas clínicos (Pydantic + JSON Mode/Structured Outputs).
2. Geração de explicação diagnóstica humanizada e contextualizada a partir do ECG (Fase 4)
   e histórico do paciente (Fase 5).
3. Tratamento robusto de exceções de rede, autenticação e cota (try/except).
4. Carregamento seguro de credenciais via variáveis de ambiente (.env).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Garante compatibilidade de saída UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, ValidationError

# ---------------------------------------------------------------------------
# 1. Carregamento de Variáveis de Ambiente (.env) e Colab Secrets
# ---------------------------------------------------------------------------
# Busca o arquivo .env no diretório atual, pai ou raiz do projeto
_base_dir = Path(__file__).resolve().parent
_env_candidatos = [
    _base_dir / ".env",
    _base_dir.parent / ".env",
    _base_dir.parent.parent / ".env",
    _base_dir.parent.parent.parent / ".env",
]
for _candidate in _env_candidatos:
    if _candidate.exists():
        load_dotenv(_candidate)
        break
else:
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv()

# Suporte automático a Google Colab Secrets
try:
    from google.colab import userdata
    if "OPENAI_API_KEY" in userdata and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
except Exception:
    pass

# Verificação opcional de bibliotecas de LLM instaladas
try:
    from openai import (
        APIConnectionError,
        AuthenticationError,
        OpenAI,
        OpenAIError,
        RateLimitError,
    )
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ---------------------------------------------------------------------------
# 2. Schemas Pydantic para Validação Estruturada
# ---------------------------------------------------------------------------
class ExtracaoClinica(BaseModel):
    """Schema para extração estruturada de relatos clínicos não estruturados."""
    sintomas: List[str] = Field(
        description="Lista de sintomas ou queixas mencionados pelo paciente"
    )
    duracao: str = Field(
        description="Duração dos sintomas (ex: '2 horas', '3 dias', 'não informado')"
    )
    intensidade: str = Field(
        description="Intensidade subjetiva: 'baixa', 'moderada' ou 'alta'"
    )
    fatores_risco: List[str] = Field(
        default_factory=list,
        description="Comorbidades e histórico (ex: hipertensão, tabagismo, arritmia prévia)"
    )
    urgencia: str = Field(
        description="Nível de urgência para triagem clínica: 'baixa', 'media' ou 'alta'"
    )
    classe_ecg_provavel: Optional[str] = Field(
        default="N",
        description="Classe provável de ECG mapeada da Fase 4 (N, S, V, F ou Q)"
    )


# Dicionário de apoio com os metadados das classes de arritmia da Fase 4
CLASSES_ECG_FASE4 = {
    "N": {
        "nome": "Batimento Normal / Sinusal",
        "severidade": "Baixa",
        "descricao": "Ritmo cardíaco sem alterações morfológicas patológicas graves detectadas."
    },
    "S": {
        "nome": "Ectopia Supraventricular",
        "severidade": "Moderada",
        "descricao": "Alteração elétrica originada acima dos ventrículos (átrios ou nó AV), frequente em palpitações e taquicardias."
    },
    "V": {
        "nome": "Ectopia Ventricular",
        "severidade": "Alta",
        "descricao": "Alteração originada nos ventrículos (ex: contrações ventriculares prematuras). Pode sinalizar isquemia ou alto risco arrítmico."
    },
    "F": {
        "nome": "Batimento de Fusão",
        "severidade": "Moderada/Alta",
        "descricao": "Combinação simultânea de despolarização supraventricular e ventricular."
    },
    "Q": {
        "nome": "Batimento Desconhecido / Ritmo com Marca-passo",
        "severidade": "Avaliação Específica",
        "descricao": "Traçado eletrocardiográfico atípico ou presença de espículas de estimulação artificial."
    }
}


# ---------------------------------------------------------------------------
# 3. Função Principal: Explicação Diagnóstica Humanizada de ECG
# ---------------------------------------------------------------------------
def gerar_explicacao_diagnostica_humanizada(
    dados_paciente: Dict[str, Any],
    dados_exame: Dict[str, Any],
    api_key: Optional[str] = None,
    modelo: str = "gpt-4o-mini",
    provedor: str = "openai",
    temperatura: float = 0.4
) -> Dict[str, Any]:
    """
    Envia os dados do paciente e o resultado do exame de ECG (gerado pelo modelo CNN da Fase 4)
    para o modelo generativo (OpenAI 'gpt-4o-mini' ou Google Gemini) e retorna uma explicação
    diagnóstica humanizada, empática, contextualizada e clinicamente orientada.

    Args:
        dados_paciente: Dicionário com informações clínicas do paciente:
            - nome (str): Nome ou identificador do paciente.
            - idade (int): Idade do paciente.
            - sexo (str): Sexo biológico.
            - historico (list[str]): Comorbidades e fatores de risco.
            - sintomas_relatados (str): Queixas e sintomas atuais.
        dados_exame: Dicionário com dados técnicos do ECG (Fase 4):
            - classe_predita (str): Classe detectada ('N', 'S', 'V', 'F', 'Q').
            - confianca (float): Confiança do classificador CNN (0.0 a 1.0).
            - frequencia_cardiaca_bpm (int): FC medida durante o traçado.
            - ritmo (str): Descrição do ritmo (ex: 'Sinusal', 'Irregular').
            - data_exame (str, opcional): Data da coleta.
        api_key: Chave da API (se None, obtém de OPENAI_API_KEY ou GEMINI_API_KEY no .env).
        modelo: Nome do modelo generativo (ex: 'gpt-4o-mini' ou 'gemini-1.5-flash').
        provedor: Provedor da API ('openai' ou 'gemini'). Auto-detectado se modelo contiver 'gemini'.
        temperatura: Temperatura para controle de criatividade (0.3 a 0.5 para precisão clínica).

    Returns:
        Dict contendo:
            - "sucesso": bool indicando se a chamada foi concluída.
            - "explicacao": str com o texto explicativo humanizado gerado pela LLM.
            - "classe_analisada": str da classe do ECG.
            - "modelo_utilizado": str do modelo que gerou a resposta.
            - "erro": str com detalhe de falha (se houver).
    """
    # Auto-detecção de provedor
    if "gemini" in modelo.lower() or provedor.lower() == "gemini":
        provedor = "gemini"
    else:
        provedor = "openai"

    # Metadados da classe detectada na Fase 4
    classe = dados_exame.get("classe_predita", "N").upper()
    info_classe = CLASSES_ECG_FASE4.get(
        classe,
        {"nome": "Classificação Não Mapeada", "severidade": "Indeterminada", "descricao": "Sem descrição específica."}
    )

    # Construção do Prompt do Sistema e do Usuário
    prompt_sistema = """Você é um médico cardiologista experiente e um comunicador de saúde empático da plataforma CardioAI.
Sua missão é explicar o resultado de um eletrocardiograma (ECG) para o paciente de forma humanizada, clara e contextualizada.

Diretrizes obrigatórias:
1. Tom de voz: Empático, acolhedor, profissional e tranquilizador, evitando alarmismo desnecessário, mas com firmeza caso haja sinais de gravidade.
2. Tradução de jargões: Não utilize termos médicos complexos sem explicá-los em linguagem simples do cotidiano.
3. Contextualização cruzada: Conecte o achado do ECG com a idade, sintomas relatados e fatores de risco prévios do paciente.
4. Plano de ação claro e prático:
   - Se for classe V com alta gravidade ou dor aguda: Oriente a buscar pronto-atendimento/SAMU 192 imediatamente com calma.
   - Se for classe S com arritmia supraventricular: Oriente agendamento e consulta com cardiologista para ajuste terapêutico.
   - Se for classe N: Reforce a normalidade do traçado, hábitos de vida saudáveis e prevenção regular.
5. Governança e Disclaimer: Inclua no final, de forma sutil e responsável, que esta explicação é um suporte educativo baseado em IA e que a avaliação médica presencial é indispensável.
"""

    prompt_usuario = f"""Por favor, gere uma explicação diagnóstica humanizada para o seguinte caso clínico:

[DADOS DO PACIENTE]
- Nome: {dados_paciente.get('nome', 'Paciente')}
- Idade: {dados_paciente.get('idade', 'Não informada')} anos | Sexo: {dados_paciente.get('sexo', 'Não informado')}
- Histórico Clínico: {', '.join(dados_paciente.get('historico', [])) if dados_paciente.get('historico') else 'Sem comorbidades relatadas'}
- Sintomas Relatados no Chat: "{dados_paciente.get('sintomas_relatados', 'Nenhum sintoma específico relatado')}"

[RESULTADOS DO ECG - FASE 04 CNN]
- Classe Predita: {classe} ({info_classe['nome']})
- Grau de Severidade Teórica: {info_classe['severidade']}
- Confiança do Modelo: {dados_exame.get('confianca', 0.0) * 100:.1f}%
- Frequência Cardíaca: {dados_exame.get('frequencia_cardiaca_bpm', 'N/D')} bpm
- Ritmo Eletrocardiográfico: {dados_exame.get('ritmo', 'N/D')}
- Descrição Técnica da Classe: {info_classe['descricao']}

Por favor, elabore a explicação em parágrafos bem estruturados e diretos para o paciente.
"""

    # -----------------------------------------------------------------------
    # Provedor Google Gemini
    # -----------------------------------------------------------------------
    if provedor == "gemini":
        if not GEMINI_AVAILABLE:
            return {
                "sucesso": False,
                "explicacao": (
                    "⚠️ O pacote 'google-generativeai' não está instalado no ambiente. "
                    "Execute 'pip install google-generativeai python-dotenv' para habilitar o Gemini."
                ),
                "erro": "ModuleNotFoundError: google.generativeai",
                "modelo_utilizado": modelo
            }

        chave_gemini = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not chave_gemini or chave_gemini.strip() in ("", "sua_chave_gemini_aqui"):
            return {
                "sucesso": False,
                "explicacao": (
                    "⚠️ Chave de API do Google Gemini não configurada. "
                    "Defina a variável GEMINI_API_KEY no arquivo .env."
                ),
                "erro": "MissingEnvironmentVariable: GEMINI_API_KEY",
                "modelo_utilizado": modelo
            }

        try:
            genai.configure(api_key=chave_gemini)
            nome_modelo_gemini = modelo if "gemini" in modelo.lower() else "gemini-1.5-flash"
            modelo_gemini = genai.GenerativeModel(
                model_name=nome_modelo_gemini,
                system_instruction=prompt_sistema
            )
            resposta = modelo_gemini.generate_content(
                prompt_usuario,
                generation_config={"temperature": temperatura, "max_output_tokens": 650}
            )
            return {
                "sucesso": True,
                "explicacao": resposta.text.strip() if resposta.text else "Nenhuma resposta gerada.",
                "classe_analisada": classe,
                "modelo_utilizado": nome_modelo_gemini,
                "erro": None
            }
        except Exception as gemini_err:
            return {
                "sucesso": False,
                "explicacao": "Erro ao processar chamada na API do Google Gemini.",
                "erro": f"GeminiAPIError: {gemini_err}",
                "modelo_utilizado": modelo
            }

    # -----------------------------------------------------------------------
    # Provedor OpenAI (gpt-4o-mini)
    # -----------------------------------------------------------------------
    if not OPENAI_AVAILABLE:
        return {
            "sucesso": False,
            "explicacao": (
                "⚠️ O pacote 'openai' não está instalado no ambiente. "
                "Execute 'pip install openai python-dotenv' para habilitar a integração real."
            ),
            "erro": "ModuleNotFoundError: openai",
            "modelo_utilizado": modelo
        }

    chave_openai = api_key or os.getenv("OPENAI_API_KEY")
    if not chave_openai or chave_openai.strip() in ("", "sua_chave_openai_aqui"):
        return {
            "sucesso": False,
            "explicacao": (
                "⚠️ Chave de API da OpenAI não configurada. "
                "Defina a variável OPENAI_API_KEY no arquivo .env ou exporte-a no ambiente."
            ),
            "erro": "MissingEnvironmentVariable: OPENAI_API_KEY",
            "modelo_utilizado": modelo
        }

    try:
        client = OpenAI(api_key=chave_openai)
        
        resposta = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=temperatura,
            max_tokens=650
        )

        conteudo = resposta.choices[0].message.content
        return {
            "sucesso": True,
            "explicacao": conteudo.strip() if conteudo else "Nenhuma resposta gerada.",
            "classe_analisada": classe,
            "modelo_utilizado": modelo,
            "tokens_utilizados": {
                "prompt": resposta.usage.prompt_tokens if resposta.usage else 0,
                "completude": resposta.usage.completion_tokens if resposta.usage else 0,
                "total": resposta.usage.total_tokens if resposta.usage else 0
            },
            "erro": None
        }

    except AuthenticationError as auth_err:
        erro_msg = f"Falha de autenticação na API: chave inválida ou sem permissão. Detalhes: {auth_err}"
        return {
            "sucesso": False,
            "explicacao": "Erro de credenciais na API de IA Generativa. Verifique a variável OPENAI_API_KEY.",
            "erro": erro_msg,
            "modelo_utilizado": modelo
        }

    except RateLimitError as rate_err:
        erro_msg = f"Limite de requisições ou cota de tokens excedida na API OpenAI: {rate_err}"
        return {
            "sucesso": False,
            "explicacao": "O serviço de IA está temporariamente sobrecarregado (rate limit/cota). Tente novamente em instantes.",
            "erro": erro_msg,
            "modelo_utilizado": modelo
        }

    except APIConnectionError as conn_err:
        erro_msg = f"Erro de conexão com os servidores da OpenAI: {conn_err}"
        return {
            "sucesso": False,
            "explicacao": "Não foi possível conectar ao servidor de IA Generativa. Verifique sua conexão de rede.",
            "erro": erro_msg,
            "modelo_utilizado": modelo
        }

    except OpenAIError as api_err:
        erro_msg = f"Erro geral na chamada da OpenAI API: {api_err}"
        return {
            "sucesso": False,
            "explicacao": "Ocorreu um erro ao processar a resposta do modelo generativo.",
            "erro": erro_msg,
            "modelo_utilizado": modelo
        }

    except Exception as general_err:
        erro_msg = f"Erro inesperado durante a geração da explicação: {general_err}"
        return {
            "sucesso": False,
            "explicacao": "Falha imprevista no processamento do laudo contextualizado.",
            "erro": erro_msg,
            "modelo_utilizado": modelo
        }


# ---------------------------------------------------------------------------
# 4. Extração Estruturada de Informações Clínicas via LLM (Fase 5)
# ---------------------------------------------------------------------------
def extrair_informacoes_clinicas_real(
    texto_clinico: str,
    api_key: Optional[str] = None,
    modelo: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Substitui a simulação mocada por extração de entidades clínicas com LLM real,
    forçando saída em JSON estrito compatível com a classe ExtracaoClinica.
    """
    if not OPENAI_AVAILABLE:
        return {"erro": "Biblioteca openai não instalada."}

    chave_resolvida = api_key or os.getenv("OPENAI_API_KEY")
    if not chave_resolvida:
        return {"erro": "Chave OPENAI_API_KEY ausente."}

    prompt_sistema = f"""Você é um assistente médico especialista em triagem cardiológica da CardioAI.
Analise a mensagem ou relato do paciente e extraia os dados estritamente no formato JSON definido pelo schema abaixo.

Mapeamento da Fase 4 (CNN ECG):
- 'N' (Normal): exames de rotina, check-up, ausência de sintomas patológicos agudos.
- 'S' (Supraventricular): palpitações, coração acelerado, taquicardias leves/moderadas.
- 'V' (Ventricular): dor no peito forte/insuportável, irradiação, falta de ar severa, alto risco.
- 'F' (Fusão) ou 'Q' (Desconhecido/Marca-passo): relatos específicos de marca-passo ou combinações complexas.

Schema JSON obrigatório:
{json.dumps(ExtracaoClinica.model_json_schema(), ensure_ascii=False, indent=2)}

Responda APENAS com o JSON válido, sem explicações adicionais ou marcações de markdown fora do JSON.
"""

    try:
        client = OpenAI(api_key=chave_resolvida)
        try:
            # Abordagem 1: OpenAI Structured Outputs com parsing nativo Pydantic
            completion = client.beta.chat.completions.parse(
                model=modelo,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": texto_clinico}
                ],
                response_format=ExtracaoClinica,
                temperature=0.1
            )
            objeto_validado = completion.choices[0].message.parsed
            if objeto_validado is not None:
                return objeto_validado.model_dump()
        except Exception:
            pass

        # Abordagem 2: Fallback padrão com json_object
        resposta = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto_clinico}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        conteudo_raw = resposta.choices[0].message.content or "{}"
        dados = json.loads(conteudo_raw)
        objeto_validado = ExtracaoClinica.model_validate(dados)
        return objeto_validado.model_dump()

    except ValidationError as val_err:
        return {"erro": f"Erro de validação de schema Pydantic: {val_err}"}
    except json.JSONDecodeError as json_err:
        return {"erro": f"Erro no parsing do JSON retornado pela LLM: {json_err}"}
    except (AuthenticationError, RateLimitError, APIConnectionError, OpenAIError) as api_err:
        return {"erro": f"Falha na API da OpenAI: {api_err}"}
    except Exception as exc:
        return {"erro": f"Erro inesperado: {exc}"}


# ---------------------------------------------------------------------------
# 5. Execução Demonstrativa e Testes Práticos
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print(" CardioAI - Fase 05: Integração Real com LLM ('gpt-4o-mini')")
    print("=" * 70)

    # Casos de teste clínicos simulando a integração Fase 4 (CNN) + Fase 5 (Watson)
    casos_clinicos = [
        {
            "descricao": "Caso 1 - Arritmia Supraventricular (Classe S)",
            "paciente": {
                "nome": "Dra. Mariana Costa",
                "idade": 42,
                "sexo": "Feminino",
                "historico": ["Crises esporádicas de ansiedade", "Episódio anterior de taquicardia"],
                "sintomas_relatados": "Sinto meu coração disparar de repente e palpitações que duram cerca de 45 minutos."
            },
            "exame": {
                "classe_predita": "S",
                "confianca": 0.894,
                "frequencia_cardiaca_bpm": 128,
                "ritmo": "Taquicardia Supraventricular paroxística",
                "data_exame": "2026-10-14"
            }
        },
        {
            "descricao": "Caso 2 - Emergência Ventricular Aguda (Classe V)",
            "paciente": {
                "nome": "Sr. Roberto Silva",
                "idade": 63,
                "sexo": "Masculino",
                "historico": ["Hipertensão arterial sistêmica", "Tabagista ativo (30 anos)"],
                "sintomas_relatados": "Dor no peito em aperto muito forte há 40 minutos, irradiando para o braço esquerdo e suor frio."
            },
            "exame": {
                "classe_predita": "V",
                "confianca": 0.957,
                "frequencia_cardiaca_bpm": 114,
                "ritmo": "Extrassístoles Ventriculares Frequentes",
                "data_exame": "2026-10-14"
            }
        },
        {
            "descricao": "Caso 3 - Eletrocardiograma Normal / Check-up (Classe N)",
            "paciente": {
                "nome": "Lucas Martins",
                "idade": 29,
                "sexo": "Masculino",
                "historico": ["Nenhum histórico cardiovascular relevante"],
                "sintomas_relatados": "Exame admissional de rotina da empresa, assintomático."
            },
            "exame": {
                "classe_predita": "N",
                "confianca": 0.991,
                "frequencia_cardiaca_bpm": 72,
                "ritmo": "Ritmo Sinusal Regular",
                "data_exame": "2026-10-14"
            }
        }
    ]

    for caso in casos_clinicos:
        print(f"\n>>> TESTANDO: {caso['descricao']}")
        resultado = gerar_explicacao_diagnostica_humanizada(
            dados_paciente=caso["paciente"],
            dados_exame=caso["exame"]
        )

        if resultado["sucesso"]:
            print(f"✅ SUCESSO ({resultado['modelo_utilizado']}) - Classe: {resultado['classe_analisada']}")
            print("-" * 70)
            print(resultado["explicacao"])
            print("-" * 70)
            if "tokens_utilizados" in resultado:
                print(f"📊 Consumo: {resultado['tokens_utilizados']}")
        else:
            print(f"❌ AVISO / FALHA TRATADA: {resultado['erro']}")
            print(f"💬 Mensagem apresentada: {resultado['explicacao']}")
