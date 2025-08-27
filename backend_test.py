#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Financial Dashboard
Tests all CRUD operations, reports, and export functionality
"""

import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any, Optional

class FinancialDashboardTester:
    def __init__(self, base_url="https://eyewear-dashboard.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_items = {
            'transactions': [],
            'clients': []
        }

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Make HTTP request and return success status and response data"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            if response.status_code in [200, 201]:
                try:
                    return True, response.json()
                except:
                    return True, {"message": "Success - No JSON response"}
            else:
                return False, {
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }

        except Exception as e:
            return False, {"error": str(e)}

    def test_api_health(self):
        """Test basic API connectivity"""
        success, response = self.make_request('GET', '')
        return self.log_test(
            "API Health Check", 
            success and "Dashboard Financeiro" in str(response),
            f"Response: {response}"
        )

    def test_dashboard_reports(self):
        """Test dashboard data endpoints"""
        # Test dashboard data
        success, response = self.make_request('GET', 'reports/dashboard')
        dashboard_ok = self.log_test(
            "Dashboard Data", 
            success and 'mes_atual' in response,
            f"Keys: {list(response.keys()) if success else response}"
        )

        # Test monthly reports
        success, response = self.make_request('GET', 'reports/monthly', params={'ano': 2024})
        monthly_ok = self.log_test(
            "Monthly Reports", 
            success and isinstance(response, list),
            f"Months returned: {len(response) if success else response}"
        )

        return dashboard_ok and monthly_ok

    def test_transaction_crud(self):
        """Test complete transaction CRUD operations"""
        # Test CREATE transaction
        transaction_data = {
            "tipo": "entrada",
            "categoria": "venda_oculos",
            "descricao": "Teste - Venda de óculos Ray-Ban",
            "valor": 450.00,
            "data": "2024-12-20",
            "cliente_nome": "Cliente Teste API",
            "observacoes": "Transação criada via teste automatizado"
        }

        success, response = self.make_request('POST', 'transactions', transaction_data)
        create_ok = self.log_test(
            "Create Transaction", 
            success and 'id' in response,
            f"ID: {response.get('id', 'N/A')}"
        )

        if not create_ok:
            return False

        transaction_id = response['id']
        self.created_items['transactions'].append(transaction_id)

        # Test READ transactions
        success, response = self.make_request('GET', 'transactions', params={'limit': 10})
        read_ok = self.log_test(
            "Read Transactions", 
            success and isinstance(response, list) and len(response) > 0,
            f"Found {len(response) if success else 0} transactions"
        )

        # Test UPDATE transaction
        update_data = {
            "valor": 500.00,
            "descricao": "Teste - Venda de óculos Ray-Ban (ATUALIZADO)"
        }
        success, response = self.make_request('PUT', f'transactions/{transaction_id}', update_data)
        update_ok = self.log_test(
            "Update Transaction", 
            success and response.get('valor') == 500.00,
            f"New value: R$ {response.get('valor', 'N/A')}"
        )

        # Test DELETE transaction
        success, response = self.make_request('DELETE', f'transactions/{transaction_id}')
        delete_ok = self.log_test(
            "Delete Transaction", 
            success,
            f"Response: {response}"
        )

        if delete_ok:
            self.created_items['transactions'].remove(transaction_id)

        return create_ok and read_ok and update_ok and delete_ok

    def test_client_crud_with_clustering_fields(self):
        """Test complete client CRUD with all clustering fields"""
        # Test CREATE client with all clustering fields
        client_data = {
            "nome": "Ana Silva Santos - Teste API",
            "email": "ana.teste@email.com",
            "telefone": "(11) 99999-9999",
            "endereco": "Rua Teste, 123 - São Paulo/SP",
            "status": "adimplente",
            "valor_devido": 150.00,
            
            # Clustering fields
            "idade": 35,
            "estado_civil": "casado",
            "numero_filhos": 2,
            "escolaridade": "superior",
            "tem_cartao_credito": True,
            "renda_bruta": 5500.00,
            "frequencia_compra": "regular",
            "quantidade_compras": 8,
            "tipo_compra": "premium",
            "origem_cliente": "instagram",
            "observacoes": "Cliente criado via teste automatizado com todos os campos de clusterização"
        }

        success, response = self.make_request('POST', 'clients', client_data)
        create_ok = self.log_test(
            "Create Client (Full Clustering)", 
            success and 'id' in response,
            f"ID: {response.get('id', 'N/A')}, Age: {response.get('idade', 'N/A')}"
        )

        if not create_ok:
            return False

        client_id = response['id']
        self.created_items['clients'].append(client_id)

        # Verify all clustering fields were saved
        clustering_fields = ['idade', 'estado_civil', 'escolaridade', 'renda_bruta', 'tipo_compra', 'origem_cliente']
        fields_ok = all(response.get(field) is not None for field in clustering_fields)
        self.log_test(
            "Clustering Fields Saved", 
            fields_ok,
            f"Fields present: {[f for f in clustering_fields if response.get(f) is not None]}"
        )

        # Test READ clients
        success, response = self.make_request('GET', 'clients')
        read_ok = self.log_test(
            "Read Clients", 
            success and isinstance(response, list) and len(response) > 0,
            f"Found {len(response) if success else 0} clients"
        )

        # Test UPDATE client (modify clustering fields)
        update_data = {
            "renda_bruta": 6000.00,
            "quantidade_compras": 12,
            "tipo_compra": "luxo",
            "frequencia_compra": "frequente"
        }
        success, response = self.make_request('PUT', f'clients/{client_id}', update_data)
        update_ok = self.log_test(
            "Update Client (Clustering)", 
            success and response.get('renda_bruta') == 6000.00 and response.get('tipo_compra') == 'luxo',
            f"New income: R$ {response.get('renda_bruta', 'N/A')}, Type: {response.get('tipo_compra', 'N/A')}"
        )

        # Test DELETE client
        success, response = self.make_request('DELETE', f'clients/{client_id}')
        delete_ok = self.log_test(
            "Delete Client", 
            success,
            f"Response: {response}"
        )

        if delete_ok:
            self.created_items['clients'].remove(client_id)

        return create_ok and fields_ok and read_ok and update_ok and delete_ok

    def test_export_functionality(self):
        """Test CSV export endpoints"""
        # Create test data first
        test_transaction = {
            "tipo": "entrada",
            "categoria": "venda_lentes",
            "descricao": "Teste Export - Lentes de contato",
            "valor": 200.00,
            "data": "2024-12-20"
        }
        
        test_client = {
            "nome": "Cliente Export Teste",
            "email": "export@teste.com",
            "idade": 28,
            "renda_bruta": 4000.00,
            "tipo_compra": "padrao"
        }

        # Create test items
        success1, trans_resp = self.make_request('POST', 'transactions', test_transaction)
        success2, client_resp = self.make_request('POST', 'clients', test_client)

        if success1:
            self.created_items['transactions'].append(trans_resp['id'])
        if success2:
            self.created_items['clients'].append(client_resp['id'])

        # Test transaction export
        success, response = self.make_request('GET', 'export/transactions')
        trans_export_ok = self.log_test(
            "Export Transactions", 
            success and 'data' in response and len(response['data']) > 0,
            f"Exported {response.get('total', 0) if success else 0} transactions"
        )

        # Verify transaction export structure
        if success and response['data']:
            expected_fields = ['ID', 'Data', 'Tipo', 'Categoria', 'Descrição', 'Valor']
            actual_fields = list(response['data'][0].keys())
            fields_ok = all(field in actual_fields for field in expected_fields)
            self.log_test(
                "Transaction Export Fields", 
                fields_ok,
                f"Fields: {actual_fields[:5]}..."
            )

        # Test client export
        success, response = self.make_request('GET', 'export/clients')
        client_export_ok = self.log_test(
            "Export Clients", 
            success and 'data' in response and len(response['data']) > 0,
            f"Exported {response.get('total', 0) if success else 0} clients"
        )

        # Verify client export includes clustering fields
        if success and response['data']:
            clustering_fields = ['Idade', 'Renda Bruta', 'Tipo de Compra', 'Estado Civil', 'Origem do Cliente']
            actual_fields = list(response['data'][0].keys())
            clustering_ok = any(field in actual_fields for field in clustering_fields)
            self.log_test(
                "Client Export Clustering Fields", 
                clustering_ok,
                f"Clustering fields found: {[f for f in clustering_fields if f in actual_fields]}"
            )

        return trans_export_ok and client_export_ok

    def test_data_filtering(self):
        """Test filtering and query parameters"""
        # Test transaction filtering by type
        success, response = self.make_request('GET', 'transactions', params={'tipo': 'entrada', 'limit': 5})
        filter_ok = self.log_test(
            "Transaction Filtering", 
            success and isinstance(response, list),
            f"Filtered results: {len(response) if success else 0}"
        )

        # Test client filtering by status
        success, response = self.make_request('GET', 'clients', params={'status': 'adimplente'})
        client_filter_ok = self.log_test(
            "Client Filtering", 
            success and isinstance(response, list),
            f"Adimplent clients: {len(response) if success else 0}"
        )

        return filter_ok and client_filter_ok

    def cleanup_test_data(self):
        """Clean up any remaining test data"""
        cleanup_count = 0
        
        # Clean up transactions
        for trans_id in self.created_items['transactions'][:]:
            success, _ = self.make_request('DELETE', f'transactions/{trans_id}')
            if success:
                cleanup_count += 1
                self.created_items['transactions'].remove(trans_id)

        # Clean up clients
        for client_id in self.created_items['clients'][:]:
            success, _ = self.make_request('DELETE', f'clients/{client_id}')
            if success:
                cleanup_count += 1
                self.created_items['clients'].remove(client_id)

        if cleanup_count > 0:
            print(f"🧹 Cleaned up {cleanup_count} test items")

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Financial Dashboard API Tests")
        print(f"📍 Testing URL: {self.base_url}")
        print("=" * 60)

        # Run all test categories
        tests = [
            ("API Health", self.test_api_health),
            ("Dashboard Reports", self.test_dashboard_reports),
            ("Transaction CRUD", self.test_transaction_crud),
            ("Client CRUD + Clustering", self.test_client_crud_with_clustering_fields),
            ("Export Functionality", self.test_export_functionality),
            ("Data Filtering", self.test_data_filtering)
        ]

        print("\n📋 Test Results:")
        print("-" * 40)

        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_test(f"{test_name} (Exception)", False, f"Error: {str(e)}")

        # Cleanup
        self.cleanup_test_data()

        # Final results
        print("\n" + "=" * 60)
        print(f"📊 FINAL RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED! Backend is working correctly.")
            return 0
        else:
            failed = self.tests_run - self.tests_passed
            print(f"⚠️  {failed} tests failed. Check the issues above.")
            return 1

def main():
    """Main test execution"""
    tester = FinancialDashboardTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())