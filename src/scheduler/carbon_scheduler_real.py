from src.scheduler.carbon_collector import collect_and_store_carbon

def run_real_carbon_scheduler(): # WattTime + 프로메테우스로 동작하는 실제버전
  nodes = ["node1", "node2", "node3"] # 실제 클러스터 노드명 리스트들임
  results = {}
  
  for node in nodes:
    emission = collect_and_store_carbon(node)
    if emission is not None:
      results[node] = emission
      
    if not results:
      print("데이터 수집 실패 혹은 지금 비어있음")
      return{
        "상태" : "실패",
        "이유" : "비어있음, 없음 둘중하나"
      }
      
    # 배출량 베스트 클러스터 선택
    optimal = min(results, key=results.get)
    print(f"베스트 클러스터 : {optimal} (배출량 {results[optimal]:.2f} gCO2)")
    return {
      "optimal_cluster" : optimal,
      "emission" : results
    }
