import re
from typing import Dict, Tuple

class LocalIntentEngine:
    """
    Motor local de intents para fallback caso o Watson Assistant falhe ou não tenha credenciais.
    Usa um sistema simples de palavras-chave simulando o comportamento básico da skill.
    """
    
    def __init__(self):
        # Mapeamento simplificado inspirado no skill-cardioia.json
        self.rules = {
            "saudacao": [r'\boi\b', r'\bolá\b', r'\bola\b', r'\bbom dia\b', r'\bboa tarde\b', r'\bboa noite\b', r'\bopa\b'],
            "emergencia": [r'\bdor.*forte\b', r'\bfalta de ar\b', r'\benfartando\b', r'\bdesmaiando\b', r'\bsocorro\b', r'\baperto\b'],
            "sintomas_cardiacos": [r'\bdor no peito\b', r'\bacelerado\b', r'\bpalpitação\b', r'\bpalpitacao\b', r'\bpressão alta\b', r'\btontura\b', r'\bbatendo forte\b'],
            "agendamento_consulta": [r'\bmarcar\b', r'\bagendar\b', r'\bconsulta\b', r'\bretorno\b', r'\bmédico\b', r'\bmedico\b'],
            "duvida_ecg": [r'\becg\b', r'\barritmia\b', r'\bfusão\b', r'\bfusao\b', r'\bresultado\b', r'\bexame\b', r'\bclasse f\b', r'\bclasse n\b', r'\bclasse q\b', r'\bclasse s\b', r'\bclasse v\b'],
            "despedida": [r'\bobrigado\b', r'\btchau\b', r'\baté mais\b', r'\bvaleu\b']
        }
        
        # Respostas para cada intent
        self.responses = {
            "saudacao": "Olá! Sou o Assistente CardioAI (Modo Local). Posso ajudar a marcar consultas, esclarecer dúvidas sobre ECG ou entender seus sintomas iniciais.\n\n⚠️ AVISO: Sou um protótipo educacional. Não realizo diagnóstico médico.",
            "emergencia": "⚠️ ATENÇÃO: Seus sintomas podem indicar uma emergência médica!\n\nLigue imediatamente para 192 (SAMU) ou procure o pronto-socorro mais próximo. Não espere.",
            "sintomas_cardiacos": "Entendi que você está relatando um sintoma. É importante que um médico avalie isso. Gostaria de agendar uma consulta presencial?\n\n(Aviso: Esta avaliação não substitui um diagnóstico médico real).",
            "agendamento_consulta": "Para agendar uma consulta com nossa equipe de cardiologia, por favor acesse a aba 'Agendamentos' no portal ou ligue para nossa central.\n(Modo demonstração: agendamento simulado).",
            "duvida_ecg": "Entendi que você tem uma dúvida sobre ECG. Vou buscar essa informação na nossa base de conhecimento (integração com Fase 4).",
            "despedida": "Obrigado por usar o CardioAI! Cuide do seu coração. Até logo!",
            "fallback": "Desculpe, não compreendi. Posso ajudar com agendamento de consultas, dúvidas sobre ECG (classes F, N, Q, S, V) ou triagem inicial de sintomas. Como posso ser útil?"
        }

    def process_message(self, message: str) -> Tuple[str, str, bool]:
        """
        Processa a mensagem e retorna (resposta, intent, is_urgent)
        """
        message_lower = message.lower()
        
        # Ordem de prioridade (emergência primeiro)
        intents_to_check = ["emergencia", "sintomas_cardiacos", "agendamento_consulta", "duvida_ecg", "saudacao", "despedida"]
        
        detected_intent = "fallback"
        
        for intent in intents_to_check:
            for pattern in self.rules[intent]:
                if re.search(pattern, message_lower):
                    detected_intent = intent
                    break
            if detected_intent != "fallback":
                break
                
        is_urgent = detected_intent == "emergencia"
        response = self.responses.get(detected_intent, self.responses["fallback"])
        
        return response, detected_intent, is_urgent
