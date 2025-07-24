#!/usr/bin/env python3
"""
Performance Testing Script for ShadowHawk Database Browser
"""

import time
import os
import pandas as pd
from fast_database_utils import FastDatabaseManager
from database_utils import DatabaseManager, DataProcessor

def create_large_test_file(filename: str, rows: int = 100000):
    """Create a large test CSV file for performance testing"""
    print(f"Creating test file with {rows:,} rows...")
    
    import random
    import string
    
    data = {
        'id': range(1, rows + 1),
        'name': [f"User_{i}_{random.choice(string.ascii_uppercase)}" for i in range(rows)],
        'email': [f"user{i}@example{random.randint(1,10)}.com" for i in range(rows)],
        'age': [random.randint(18, 80) for _ in range(rows)],
        'city': [random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
                               'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Austin']) 
                for _ in range(rows)],
        'salary': [random.randint(30000, 150000) for _ in range(rows)],
        'department': [random.choice(['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']) 
                      for _ in range(rows)],
        'description': [f"This is a description for user {i} with some random text " + 
                       ''.join(random.choices(string.ascii_letters, k=50)) 
                       for i in range(rows)]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    
    file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
    print(f"✅ Created {filename} ({file_size:.1f} MB)")
    
    return filename

def test_import_performance():
    """Test import performance comparison"""
    print("\n🚀 IMPORT PERFORMANCE TEST")
    print("=" * 50)
    
    # Create test file
    test_file = "performance_test.csv"
    create_large_test_file(test_file, 100000)
    
    try:
        # Test standard import
        print("\n📊 Standard Import:")
        start_time = time.time()
        
        standard_manager = DatabaseManager()
        conn1, table1 = standard_manager.load_csv_as_database(test_file)
        
        standard_time = time.time() - start_time
        print(f"  Time: {standard_time:.2f} seconds")
        
        # Test fast import
        print("\n⚡ Fast Import:")
        start_time = time.time()
        
        fast_manager = FastDatabaseManager()
        conn2, table2 = fast_manager.load_csv_fast(test_file)
        
        fast_time = time.time() - start_time
        print(f"  Time: {fast_time:.2f} seconds")
        
        # Performance improvement
        improvement = ((standard_time - fast_time) / standard_time) * 100
        print(f"\n📈 Performance Improvement: {improvement:.1f}% faster")
        print(f"   Speed ratio: {standard_time/fast_time:.1f}x")
        
        return conn1, table1, conn2, table2
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

def test_search_performance(conn1, table1, conn2, table2):
    """Test search performance comparison"""
    print("\n🔍 SEARCH PERFORMANCE TEST")
    print("=" * 50)
    
    search_terms = ["User_1", "Engineering", "example1.com", "New York", "50000"]
    
    for search_term in search_terms:
        print(f"\nSearching for: '{search_term}'")
        
        # Standard search
        start_time = time.time()
        df1 = pd.read_sql_query(f"SELECT * FROM {table1}", conn1)
        processor = DataProcessor()
        results1 = processor.search_dataframe(df1, search_term)
        standard_time = time.time() - start_time
        
        # Fast search
        start_time = time.time()
        fast_manager = FastDatabaseManager()
        results2 = fast_manager.fast_search_table(conn2, table2, search_term)
        fast_time = time.time() - start_time
        
        print(f"  📊 Standard: {len(results1):,} matches in {standard_time:.3f}s")
        print(f"  ⚡ Fast:     {len(results2):,} matches in {fast_time:.3f}s")
        
        if fast_time > 0:
            speedup = standard_time / fast_time
            print(f"  📈 Speedup: {speedup:.1f}x faster")

def test_parallel_search():
    """Test parallel vs sequential search"""
    print("\n🌐 PARALLEL SEARCH TEST")
    print("=" * 50)
    
    # Create multiple small test databases
    test_files = []
    databases = {}
    
    try:
        for i in range(5):
            filename = f"test_db_{i}.csv"
            create_large_test_file(filename, 20000)
            test_files.append(filename)
            
            # Load into fast manager
            fast_manager = FastDatabaseManager()
            conn, table = fast_manager.load_csv_fast(filename)
            
            databases[filename] = {
                'connection': conn,
                'type': 'sqlite',
                'tables': [table]
            }
        
        search_term = "User_1"
        
        # Sequential search (simulated)
        print(f"\nSearching '{search_term}' across {len(databases)} databases:")
        
        start_time = time.time()
        total_matches = 0
        for db_name, db_info in databases.items():
            conn = db_info['connection']
            table = db_info['tables'][0]
            fast_manager = FastDatabaseManager()
            results = fast_manager.fast_search_table(conn, table, search_term)
            total_matches += len(results)
        sequential_time = time.time() - start_time
        
        # Parallel search
        start_time = time.time()
        fast_manager = FastDatabaseManager()
        parallel_results = fast_manager.parallel_global_search(databases, search_term)
        parallel_time = time.time() - start_time
        
        print(f"  📊 Sequential: {total_matches:,} matches in {sequential_time:.3f}s")
        print(f"  ⚡ Parallel:   {parallel_results['total_matches']:,} matches in {parallel_time:.3f}s")
        
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
            print(f"  📈 Parallel speedup: {speedup:.1f}x faster")
        
    finally:
        # Cleanup
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)

def main():
    """Run all performance tests"""
    print("🚀 ShadowHawk Database Browser - Performance Tests")
    print("=" * 60)
    
    try:
        # Test import performance
        conn1, table1, conn2, table2 = test_import_performance()
        
        # Test search performance
        test_search_performance(conn1, table1, conn2, table2)
        
        # Test parallel search
        test_parallel_search()
        
        print("\n✅ All performance tests completed!")
        print("\n📊 SUMMARY:")
        print("  ⚡ Fast imports use chunked processing and data type optimization")
        print("  🔍 Fast search uses database indexes and SQL queries")
        print("  🌐 Parallel search uses multiple threads for concurrent operations")
        print("  📈 Expected improvements: 2-5x faster imports, 3-10x faster searches")
        
    except Exception as e:
        print(f"\n❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
