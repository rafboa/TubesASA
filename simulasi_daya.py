import time
import random
import heapq

# 1. GENERATE DATA SIMULASI
def generate_data(n):
    """Menghasilkan list objek proses dengan nilai (1-10) dan daya (50-1500 mW)."""
    random.seed(42) 
    values = [random.randint(1, 10) for _ in range(n)]
    weights = [random.randint(50, 1500) for _ in range(n)]
    return values, weights

# 2. ALGORITMA DYNAMIC PROGRAMMING 
def knapsack_dp(W, weights, values, n):
    # Membuat matriks K berukuran (n+1) x (W+1)
    K = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
    
    for i in range(n + 1):
        for w in range(W + 1):
            if i == 0 or w == 0:
                K[i][w] = 0
            elif weights[i-1] <= w:
                K[i][w] = max(values[i-1] + K[i-1][w-weights[i-1]], K[i-1][w])
            else:
                K[i][w] = K[i-1][w]
                
    return K[n][W]

# 3. ALGORITMA BRANCH AND BOUND 
class Node:
    def __init__(self, level, profit, weight, bound):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = bound
        
    def __lt__(self, other):
        # Max-Heap berdasarkan bound
        return self.bound > other.bound

def bound(u, n, W, items):
    if u.weight >= W:
        return 0
    profit_bound = u.profit
    j = u.level + 1
    totweight = u.weight
    
    while j < n and totweight + items[j]['w'] <= W:
        totweight += items[j]['w']
        profit_bound += items[j]['v']
        j += 1
        
    if j < n:
        profit_bound += (W - totweight) * items[j]['v'] / items[j]['w']
        
    return profit_bound

def knapsack_bnb(W, weights, values, n):
    # Gabungkan menjadi list of dictionary lalu urutkan berdasarkan v/w
    items = [{'v': values[i], 'w': weights[i]} for i in range(n)]
    items.sort(key=lambda x: x['v']/x['w'], reverse=True)
    
    Q = []
    u = Node(-1, 0, 0, 0)
    v = Node(-1, 0, 0, 0)
    
    max_profit = 0
    u.bound = bound(u, n, W, items)
    heapq.heappush(Q, u)
    
    while Q:
        u = heapq.heappop(Q)
        
        if u.bound > max_profit and u.level < n - 1:
            v.level = u.level + 1
            
            # Skenario 1: Mengambil item
            v.weight = u.weight + items[v.level]['w']
            v.profit = u.profit + items[v.level]['v']
            
            if v.weight <= W and v.profit > max_profit:
                max_profit = v.profit
                
            v.bound = bound(v, n, W, items)
            if v.bound > max_profit:
                heapq.heappush(Q, Node(v.level, v.profit, v.weight, v.bound))
                
            # Skenario 2: Tidak mengambil item
            v.weight = u.weight
            v.profit = u.profit
            v.bound = bound(v, n, W, items)
            if v.bound > max_profit:
                heapq.heappush(Q, Node(v.level, v.profit, v.weight, v.bound))
                
    return max_profit

# 4. ALGORITMA HILL CLIMBING 
def get_profit_weight(solution, values, weights):
    p = sum(values[i] for i in range(len(solution)) if solution[i] == 1)
    w = sum(weights[i] for i in range(len(solution)) if solution[i] == 1)
    return p, w

def knapsack_hc(W, weights, values, n):
    # Inisialisasi status acak yang valid
    current_solution = [0] * n
    current_profit = 0
    current_weight = 0
    
    while True:
        best_neighbor = list(current_solution)
        best_profit = current_profit
        best_weight = current_weight
        found_better = False
        
        # Cek semua tetangga 
        for i in range(n):
            neighbor = list(current_solution)
            neighbor[i] = 1 - neighbor[i] 
            
            p, w = get_profit_weight(neighbor, values, weights)
            
            # Jika profit lebih tinggi dan tidak melebihi kapasitas daya sistem
            if w <= W and p > best_profit:
                best_profit = p
                best_weight = w
                best_neighbor = list(neighbor)
                found_better = True
                
        if found_better:
            current_solution = best_neighbor
            current_profit = best_profit
            current_weight = best_weight
        else:
            break 
            
    return current_profit

# 5. FUNGSI UTAMA 
def run_benchmark():
    W = 3000 
    skala_data = [10, 50, 100]
    
    print("="*60)
    print(f"BENCHMARKING OPTIMASI POWER STATE (Kapasitas = {W} mW)")
    print("="*60)
    
    for n in skala_data:
        values, weights = generate_data(n)
        print(f"\n[ SKALA DATA N = {n} PROSES ]")
        
        # Benchmark DP
        start = time.perf_counter()
        profit_dp = knapsack_dp(W, weights, values, n)
        time_dp = (time.perf_counter() - start) * 1000
        
        # Benchmark BnB
        start = time.perf_counter()
        profit_bnb = knapsack_bnb(W, weights, values, n)
        time_bnb = (time.perf_counter() - start) * 1000
        
        # Benchmark HC
        start = time.perf_counter()
        profit_hc = knapsack_hc(W, weights, values, n)
        time_hc = (time.perf_counter() - start) * 1000
        
        # Hitung Optimality Gap
        gap = ((profit_dp - profit_hc) / profit_dp) * 100 if profit_dp > 0 else 0
        
        print(f"{'Algoritma':<20} | {'Waktu (ms)':<12} | {'Profit (Utilitas)':<15}")
        print("-" * 55)
        print(f"{'Dynamic Prog (DP)':<20} | {time_dp:<12.4f} | {profit_dp:<15}")
        print(f"{'Branch & Bound (BnB)':<20} | {time_bnb:<12.4f} | {profit_bnb:<15}")
        print(f"{'Hill Climbing (HC)':<20} | {time_hc:<12.4f} | {profit_hc:<15}")
        print(f"-> Optimality Gap HC : {gap:.2f} %")

if __name__ == "__main__":
    run_benchmark()
