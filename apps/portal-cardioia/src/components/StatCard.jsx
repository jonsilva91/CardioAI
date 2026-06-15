import styles from "./StatCard.module.css";

export default function StatCard({ title, value, subtitle }) {
  return (
    <div className={styles.card}>
      <p className={styles.title}>{title}</p>
      <h3 className={styles.value}>{value}</h3>
      <span className={styles.subtitle}>{subtitle}</span>
    </div>
  );
}
