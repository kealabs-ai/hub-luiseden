#!/usr/bin/env python3
"""
Script de teste rápido para validar o módulo fiscal
Uso: python test_quick.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = "seu-token-jwt-aqui"  # Substituir com token real

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_health():
    """Teste 1: Health check"""
    print("\n🔍 Teste 1: Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status: {resp.status_code}")
        print(f"   Resposta: {resp.json()}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_status_sefaz():
    """Teste 2: Status SEFAZ"""
    print("\n🔍 Teste 2: Status SEFAZ")
    try:
        resp = requests.get(f"{BASE_URL}/v1/eden/fiscal/status-sefaz", headers=HEADERS, timeout=10)
        print(f"✅ Status: {resp.status_code}")
        data = resp.json()
        print(f"   SEFAZ Status: {data.get('cstat')}")
        print(f"   Motivo: {data.get('xmotivo')}")
        return data.get('status') == 'sucesso'
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_criar_configuracao():
    """Teste 3: Criar configuração fiscal"""
    print("\n🔍 Teste 3: Criar Configuração Fiscal")
    try:
        config = {
            "empresaId": "empresa-teste-001",
            "cnpj": "12.345.678/0001-90",
            "razaoSocial": "Luis Eden Paisagismo LTDA",
            "nomeFantasia": "Luis Eden",
            "inscricaoEstadual": "123.456.789.012",
            "certificadoPath": "/etc/ssl/certs/empresa.pfx",
            "certificadoSenha": "senha-teste"
        }
        resp = requests.post(
            f"{BASE_URL}/v1/eden/fiscal/configuracao",
            json=config,
            headers=HEADERS,
            timeout=5
        )
        print(f"✅ Status: {resp.status_code}")
        data = resp.json()
        print(f"   Config ID: {data.get('id')}")
        print(f"   Status: {data.get('status')}")
        return resp.status_code == 201
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_obter_configuracao():
    """Teste 4: Obter configuração fiscal"""
    print("\n🔍 Teste 4: Obter Configuração Fiscal")
    try:
        resp = requests.get(
            f"{BASE_URL}/v1/eden/fiscal/configuracao/empresa-teste-001",
            headers=HEADERS,
            timeout=5
        )
        print(f"✅ Status: {resp.status_code}")
        data = resp.json()
        print(f"   CNPJ: {data.get('cnpj')}")
        print(f"   Razão Social: {data.get('razaoSocial')}")
        print(f"   Próximo Número: {data.get('proximoNumero')}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_criar_nfe():
    """Teste 5: Criar NF-e"""
    print("\n🔍 Teste 5: Criar NF-e")
    try:
        nfe = {
            "clienteId": "cliente-teste-001",
            "dataEmissao": datetime.utcnow().isoformat(),
            "itens": [
                {
                    "produtoId": "produto-001",
                    "descricao": "Serviço de Paisagismo",
                    "quantidade": 1,
                    "valorUnitarioCents": 500000,
                    "ncm": "92110000",
                    "cfop": "5102"
                }
            ]
        }
        resp = requests.post(
            f"{BASE_URL}/v1/eden/fiscal/nfe",
            json=nfe,
            headers=HEADERS,
            timeout=5
        )
        print(f"✅ Status: {resp.status_code}")
        data = resp.json()
        print(f"   NF-e ID: {data.get('id')}")
        print(f"   Número: {data.get('numero')}")
        print(f"   Status: {data.get('status')}")
        return resp.status_code == 201, data.get('id')
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False, None

def test_obter_nfe(nfe_id):
    """Teste 6: Obter dados da NF-e"""
    print("\n🔍 Teste 6: Obter Dados da NF-e")
    try:
        resp = requests.get(
            f"{BASE_URL}/v1/eden/fiscal/nfe/{nfe_id}",
            headers=HEADERS,
            timeout=5
        )
        print(f"✅ Status: {resp.status_code}")
        data = resp.json()
        print(f"   Número: {data.get('numero')}")
        print(f"   Cliente ID: {data.get('clienteId')}")
        print(f"   Valor Total: R$ {data.get('valorTotalCents')/100:.2f}")
        print(f"   Status: {data.get('status')}")
        print(f"   Itens: {len(data.get('itens', []))}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_assinar_nfe(nfe_id):
    """Teste 7: Assinar NF-e"""
    print("\n🔍 Teste 7: Assinar NF-e")
    try:
        resp = requests.post(
            f"{BASE_URL}/v1/eden/fiscal/nfe/assinar",
            json={"notaFiscalId": nfe_id},
            headers=HEADERS,
            timeout=10
        )
        print(f"✅ Status: {resp.status_code}")
        data = resp.json()
        print(f"   Status: {data.get('status')}")
        print(f"   NF-e ID: {data.get('nfeId')}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_autorizar_nfe(nfe_id):
    """Teste 8: Autorizar NF-e"""
    print("\n🔍 Teste 8: Autorizar NF-e")
    try:
        resp = requests.post(
            f"{BASE_URL}/v1/eden/fiscal/nfe/autorizar",
            json={"notaFiscalId": nfe_id},
            headers=HEADERS,
            timeout=30
        )
        print(f"✅ Status: {resp.status_code}")
        data = resp.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Número Recibo: {data.get('numeroRecibo')}")
        print(f"   cstat: {data.get('cstat')}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("=" * 60)
    print("🧪 TESTE RÁPIDO - MÓDULO FISCAL SEFAZ-MG")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Health
    results.append(("Health Check", test_health()))
    
    # Teste 2: Status SEFAZ
    results.append(("Status SEFAZ", test_status_sefaz()))
    
    # Teste 3: Criar Configuração
    results.append(("Criar Configuração", test_criar_configuracao()))
    
    # Teste 4: Obter Configuração
    results.append(("Obter Configuração", test_obter_configuracao()))
    
    # Teste 5: Criar NF-e
    success, nfe_id = test_criar_nfe()
    results.append(("Criar NF-e", success))
    
    if nfe_id:
        # Teste 6: Obter NF-e
        results.append(("Obter NF-e", test_obter_nfe(nfe_id)))
        
        # Teste 7: Assinar NF-e
        results.append(("Assinar NF-e", test_assinar_nfe(nfe_id)))
        
        # Teste 8: Autorizar NF-e
        results.append(("Autorizar NF-e", test_autorizar_nfe(nfe_id)))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} testes passaram")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 Todos os testes passaram!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
