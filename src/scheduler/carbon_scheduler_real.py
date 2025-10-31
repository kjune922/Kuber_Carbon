from src.db import SessionLocal, ClusterStatus
from datetime import datetime
import boto3

def run_real_carbon_scheduler():
    """
    Caspian 기반 스케줄링 알고리즘 (한국/일본 클러스터 비교)
    기준: CPU, 메모리, 탄소 배출량, 네트워크 지연(latency)
    """
    session = SessionLocal()
    try:
        clusters = session.query(ClusterStatus).all()
        if not clusters:
            print("[run_real_carbon_scheduler] No cluster data available.")
            return {"message": "No cluster data available."}

        # 가중치 (Caspian 기반)
        alpha = 0.3   # CPU usage weight
        beta = 0.2    # Memory usage weight
        gamma = 0.4   # Carbon intensity weight
        delta = 0.1   # Network latency weight

        def caspian_score(c):
            score = (
                alpha * c.cpu_usage +
                beta * c.memory_usage +
                gamma * c.carbon_intensity +
                delta * getattr(c, "network_latency", 0)
            )
            return score

        # 최적 클러스터 선택
        best_cluster = min(clusters, key=caspian_score)

        # CloudWatch로 모든 클러스터 데이터 푸시
        for c in clusters:
            push_metrics_to_cloudwatch(
                c.cluster_name,
                getattr(c, "region", "unknown"),
                c.cpu_usage,
                c.memory_usage,
                c.carbon_intensity,
                round(caspian_score(c), 4)
            )

        result = {
            "selected_cluster": best_cluster.cluster_name,
            "region": getattr(best_cluster, "region", "unknown"),
            "cpu_usage": best_cluster.cpu_usage,
            "memory_usage": best_cluster.memory_usage,
            "carbon_intensity": best_cluster.carbon_intensity,
            "network_latency": getattr(best_cluster, "network_latency", 0),
            "score": round(caspian_score(best_cluster), 4),
            "selected_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

        print(f"[Caspian Scheduler]  Selected cluster: {best_cluster.cluster_name} ({result['region']}) | Score={result['score']}")
        return result

    except Exception as e:
        print(f"[Caspian Scheduler]  Error: {e}")
        return {"error": str(e)}

    finally:
        session.close()


def push_metrics_to_cloudwatch(cluster_name, region, cpu, memory, carbon, score):
    """AWS CloudWatch 커스텀 메트릭 전송"""
    try:
        cloudwatch = boto3.client("cloudwatch", region_name="ap-northeast-2")
        print(f"[CloudWatch] Initialized in region: ap-northeast-2")

        cloudwatch.put_metric_data(
            Namespace="Kuberzo/Cluster",
            MetricData=[
                {
                    "MetricName": "CPUUsage",
                    "Dimensions": [{"Name": "Cluster", "Value": cluster_name}],
                    "Value": cpu,
                    "Unit": "Percent"
                },
                {
                    "MetricName": "MemoryUsage",
                    "Dimensions": [{"Name": "Cluster", "Value": cluster_name}],
                    "Value": memory,
                    "Unit": "Percent"
                },
                {
                    "MetricName": "CarbonIntensity",
                    "Dimensions": [{"Name": "Region", "Value": region}],
                    "Value": carbon,
                    "Unit": "None"
                },
                {
                    "MetricName": "CaspianScore",
                    "Dimensions": [{"Name": "Cluster", "Value": cluster_name}],
                    "Value": score,
                    "Unit": "None"
                }
            ]
        )

        print(f"[CloudWatch] Metrics pushed for {cluster_name} ({region})")

    except Exception as e:
        print(f"[CloudWatch] Metric push error: {e}")
