import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configuração de cores para o tema preto e dourado
const COLORS = {
  primary: '#FFD700',
  secondary: '#FFA500', 
  background: '#0D0D0D',
  cardBg: '#1A1A1A',
  textPrimary: '#FFFFFF',
  textSecondary: '#CCCCCC',
  accent: '#B8860B'
};

const CHART_COLORS = ['#FFD700', '#FFA500', '#B8860B', '#DAA520', '#F4A460'];

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [monthlyData, setMonthlyData] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);

  // Estados para formularios
  const [transactionForm, setTransactionForm] = useState({
    tipo: 'entrada',
    categoria: 'venda_oculos',
    descricao: '',
    valor: '',
    data: new Date().toISOString().split('T')[0],
    cliente_nome: '',
    observacoes: ''
  });

  const [clientForm, setClientForm] = useState({
    nome: '',
    email: '',
    telefone: '',
    endereco: '',
    status: 'adimplente',
    valor_devido: '',
    observacoes: ''
  });

  // Categorias organizadas
  const categorias = {
    entrada: {
      venda_oculos: 'Venda de Óculos',
      venda_lentes: 'Venda de Lentes',
      venda_acessorios: 'Venda de Acessórios',
      servico_exame: 'Serviço de Exame',
      servico_consulta: 'Serviço de Consulta',
      outros_servicos: 'Outros Serviços'
    },
    saida: {
      custo_produtos: 'Custo de Produtos',
      aluguel: 'Aluguel',
      salarios: 'Salários',
      energia: 'Energia Elétrica',
      agua: 'Água',
      telefone: 'Telefone/Internet',
      marketing: 'Marketing',
      manutencao: 'Manutenção',
      impostos: 'Impostos',
      outros_custos: 'Outros Custos'
    }
  };

  // Carregar dados
  useEffect(() => {
    loadDashboardData();
    loadMonthlyReports();
    loadTransactions();
    loadClients();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/reports/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    }
  };

  const loadMonthlyReports = async () => {
    try {
      const currentYear = new Date().getFullYear();
      const response = await axios.get(`${API}/reports/monthly?ano=${currentYear}`);
      
      // Preencher meses vazios
      const monthNames = [
        'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
      ];
      
      const completeData = monthNames.map((name, index) => {
        const month = index + 1;
        const existing = response.data.find(item => item.mes === month);
        return existing ? {
          ...existing,
          nome_mes: name
        } : {
          mes: month,
          nome_mes: name,
          total_entradas: 0,
          total_saidas: 0,
          faturamento_liquido: 0,
          transacoes_count: 0
        };
      });
      
      setMonthlyData(completeData);
    } catch (error) {
      console.error('Erro ao carregar relatórios mensais:', error);
    }
  };

  const loadTransactions = async () => {
    try {
      const response = await axios.get(`${API}/transactions?limit=50`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Erro ao carregar transações:', error);
    }
  };

  const loadClients = async () => {
    try {
      const response = await axios.get(`${API}/clients`);
      setClients(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
      setLoading(false);
    }
  };

  const handleTransactionSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = {
        ...transactionForm,
        valor: parseFloat(transactionForm.valor)
      };
      
      await axios.post(`${API}/transactions`, formData);
      
      // Limpar formulário
      setTransactionForm({
        tipo: 'entrada',
        categoria: 'venda_oculos',
        descricao: '',
        valor: '',
        data: new Date().toISOString().split('T')[0],
        cliente_nome: '',
        observacoes: ''
      });
      
      // Recarregar dados
      loadDashboardData();
      loadMonthlyReports();
      loadTransactions();
      
      alert('Transação adicionada com sucesso!');
    } catch (error) {
      console.error('Erro ao adicionar transação:', error);
      alert('Erro ao adicionar transação!');
    }
  };

  const handleClientSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = {
        ...clientForm,
        valor_devido: parseFloat(clientForm.valor_devido || 0)
      };
      
      await axios.post(`${API}/clients`, formData);
      
      // Limpar formulário
      setClientForm({
        nome: '',
        email: '',
        telefone: '',
        endereco: '',
        status: 'adimplente',
        valor_devido: '',
        observacoes: ''
      });
      
      loadClients();
      alert('Cliente adicionado com sucesso!');
    } catch (error) {
      console.error('Erro ao adicionar cliente:', error);
      alert('Erro ao adicionar cliente!');
    }
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (window.confirm('Tem certeza que deseja deletar esta transação?')) {
      try {
        await axios.delete(`${API}/transactions/${transactionId}`);
        alert('Transação deletada com sucesso!');
        
        // Recarregar dados
        loadDashboardData();
        loadMonthlyReports();
        loadTransactions();
      } catch (error) {
        console.error('Erro ao deletar transação:', error);
        alert('Erro ao deletar transação!');
      }
    }
  };

  const handleDeleteClient = async (clientId) => {
    if (window.confirm('Tem certeza que deseja deletar este cliente?')) {
      try {
        await axios.delete(`${API}/clients/${clientId}`);
        alert('Cliente deletado com sucesso!');
        
        // Recarregar dados
        loadClients();
        loadDashboardData();
      } catch (error) {
        console.error('Erro ao deletar cliente:', error);
        alert('Erro ao deletar cliente!');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-yellow-400 text-xl">Carregando dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-black border-b border-yellow-400 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-3xl font-bold text-yellow-400">💰 Dashboard Financeiro</h1>
                <p className="text-yellow-200 text-sm">Ótica - Gestão Profissional</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
              { id: 'transacoes', label: '💳 Transações', icon: '💳' },
              { id: 'inadimplentes', label: '⚠️ Inadimplentes', icon: '⚠️' },
              { id: 'relatorios', label: '📈 Relatórios', icon: '📈' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'border-yellow-400 text-yellow-400'
                    : 'border-transparent text-gray-300 hover:text-yellow-200 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* KPIs Cards */}
            {dashboardData && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 rounded-lg p-6 border border-yellow-400">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">↗</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-300 truncate">
                          Entradas do Mês
                        </dt>
                        <dd className="text-lg font-medium text-yellow-400">
                          R$ {dashboardData.mes_atual.entradas.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-6 border border-yellow-400">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">↙</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-300 truncate">
                          Saídas do Mês
                        </dt>
                        <dd className="text-lg font-medium text-yellow-400">
                          R$ {dashboardData.mes_atual.saidas.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-6 border border-yellow-400">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className={`w-8 h-8 ${dashboardData.mes_atual.faturamento_liquido >= 0 ? 'bg-yellow-500' : 'bg-red-500'} rounded-full flex items-center justify-center`}>
                        <span className="text-white font-bold">💰</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-300 truncate">
                          Faturamento Líquido
                        </dt>
                        <dd className={`text-lg font-medium ${dashboardData.mes_atual.faturamento_liquido >= 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                          R$ {dashboardData.mes_atual.faturamento_liquido.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Gráfico de Linha - Evolução Mensal */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-medium text-yellow-400 mb-4">📈 Evolução Mensal</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="nome_mes" 
                      stroke="#9CA3AF"
                      fontSize={12}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tickFormatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #FCD34D',
                        borderRadius: '8px',
                        color: '#FFFFFF'
                      }}
                      formatter={(value) => [`R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`, '']}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="total_entradas" 
                      stroke="#10B981" 
                      strokeWidth={3}
                      name="Entradas"
                      dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="total_saidas" 
                      stroke="#EF4444" 
                      strokeWidth={3}
                      name="Saídas"
                      dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="faturamento_liquido" 
                      stroke="#FCD34D" 
                      strokeWidth={3}
                      name="Faturamento Líquido"
                      dot={{ fill: '#FCD34D', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Gráfico de Barras - Comparação */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-medium text-yellow-400 mb-4">📊 Comparação Mensal</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="nome_mes" 
                      stroke="#9CA3AF"
                      fontSize={12}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tickFormatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #FCD34D',
                        borderRadius: '8px',
                        color: '#FFFFFF'
                      }}
                      formatter={(value) => [`R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`, '']}
                    />
                    <Legend />
                    <Bar 
                      dataKey="total_entradas" 
                      fill="#10B981" 
                      name="Entradas"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar 
                      dataKey="total_saidas" 
                      fill="#EF4444" 
                      name="Saídas"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'transacoes' && (
          <div className="space-y-6">
            {/* Formulário de Nova Transação */}
            <div className="bg-gray-800 rounded-lg p-6 border border-yellow-400">
              <h3 className="text-lg font-medium text-yellow-400 mb-4">➕ Nova Transação</h3>
              <form onSubmit={handleTransactionSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Tipo
                  </label>
                  <select
                    value={transactionForm.tipo}
                    onChange={(e) => setTransactionForm({
                      ...transactionForm, 
                      tipo: e.target.value,
                      categoria: e.target.value === 'entrada' ? 'venda_oculos' : 'custo_produtos'
                    })}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                  >
                    <option value="entrada">🟢 Entrada</option>
                    <option value="saida">🔴 Saída</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Categoria
                  </label>
                  <select
                    value={transactionForm.categoria}
                    onChange={(e) => setTransactionForm({...transactionForm, categoria: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                  >
                    {Object.entries(categorias[transactionForm.tipo]).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Valor (R$)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={transactionForm.valor}
                    onChange={(e) => setTransactionForm({...transactionForm, valor: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Data
                  </label>
                  <input
                    type="date"
                    value={transactionForm.data}
                    onChange={(e) => setTransactionForm({...transactionForm, data: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Descrição
                  </label>
                  <input
                    type="text"
                    value={transactionForm.descricao}
                    onChange={(e) => setTransactionForm({...transactionForm, descricao: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Cliente (opcional)
                  </label>
                  <input
                    type="text"
                    value={transactionForm.cliente_nome}
                    onChange={(e) => setTransactionForm({...transactionForm, cliente_nome: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                  />
                </div>

                <div className="md:col-span-2 lg:col-span-3">
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Observações
                  </label>
                  <textarea
                    value={transactionForm.observacoes}
                    onChange={(e) => setTransactionForm({...transactionForm, observacoes: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                    rows="2"
                  />
                </div>

                <div className="md:col-span-2 lg:col-span-3">
                  <button
                    type="submit"
                    className="w-full md:w-auto px-6 py-2 bg-yellow-500 text-black font-medium rounded-md hover:bg-yellow-400 transition-colors duration-200"
                  >
                    ➕ Adicionar Transação
                  </button>
                </div>
              </form>
            </div>

            {/* Lista de Transações Recentes */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-medium text-yellow-400 mb-4">📋 Transações Recentes</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Data
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Tipo
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Categoria
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Descrição
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Valor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Cliente
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-gray-800 divide-y divide-gray-700">
                    {transactions.map((transaction) => (
                      <tr key={transaction.id} className="hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          {new Date(transaction.data).toLocaleDateString('pt-BR')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            transaction.tipo === 'entrada' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {transaction.tipo === 'entrada' ? '🟢 Entrada' : '🔴 Saída'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          {categorias[transaction.tipo][transaction.categoria]}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-300">
                          {transaction.descricao}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-yellow-400">
                          R$ {transaction.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          {transaction.cliente_nome || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => handleDeleteTransaction(transaction.id)}
                            className="text-red-400 hover:text-red-300 font-medium hover:bg-red-900 hover:bg-opacity-20 px-3 py-1 rounded-md transition-colors duration-200"
                            title="Deletar transação"
                          >
                            🗑️ Deletar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inadimplentes' && (
          <div className="space-y-6">
            {/* Formulário de Novo Cliente */}
            <div className="bg-gray-800 rounded-lg p-6 border border-red-400">
              <h3 className="text-lg font-medium text-red-400 mb-4">👤 Novo Cliente</h3>
              <form onSubmit={handleClientSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Nome *
                  </label>
                  <input
                    type="text"
                    value={clientForm.nome}
                    onChange={(e) => setClientForm({...clientForm, nome: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={clientForm.email}
                    onChange={(e) => setClientForm({...clientForm, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Telefone
                  </label>
                  <input
                    type="tel"
                    value={clientForm.telefone}
                    onChange={(e) => setClientForm({...clientForm, telefone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Status
                  </label>
                  <select
                    value={clientForm.status}
                    onChange={(e) => setClientForm({...clientForm, status: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                  >
                    <option value="adimplente">✅ Adimplente</option>
                    <option value="inadimplente">⚠️ Inadimplente</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Valor Devido (R$)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={clientForm.valor_devido}
                    onChange={(e) => setClientForm({...clientForm, valor_devido: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Endereço
                  </label>
                  <input
                    type="text"
                    value={clientForm.endereco}
                    onChange={(e) => setClientForm({...clientForm, endereco: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Observações
                  </label>
                  <textarea
                    value={clientForm.observacoes}
                    onChange={(e) => setClientForm({...clientForm, observacoes: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-red-400"
                    rows="2"
                  />
                </div>

                <div className="md:col-span-2">
                  <button
                    type="submit"
                    className="w-full md:w-auto px-6 py-2 bg-red-500 text-white font-medium rounded-md hover:bg-red-400 transition-colors duration-200"
                  >
                    👤 Adicionar Cliente
                  </button>
                </div>
              </form>
            </div>

            {/* Lista de Clientes */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-medium text-yellow-400 mb-4">👥 Lista de Clientes</h3>
              
              {/* Filtros */}
              <div className="mb-4 flex flex-wrap gap-2">
                <button className="px-3 py-1 bg-gray-700 text-yellow-400 rounded-md text-sm hover:bg-gray-600">
                  Todos ({clients.length})
                </button>
                <button className="px-3 py-1 bg-gray-700 text-green-400 rounded-md text-sm hover:bg-gray-600">
                  Adimplentes ({clients.filter(c => c.status === 'adimplente').length})
                </button>
                <button className="px-3 py-1 bg-gray-700 text-red-400 rounded-md text-sm hover:bg-gray-600">
                  Inadimplentes ({clients.filter(c => c.status === 'inadimplente').length})
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Nome
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Valor Devido
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Telefone
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Email
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-gray-800 divide-y divide-gray-700">
                    {clients.map((client) => (
                      <tr key={client.id} className="hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-300">
                          {client.nome}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            client.status === 'adimplente' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {client.status === 'adimplente' ? '✅ Adimplente' : '⚠️ Inadimplente'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-400">
                          R$ {client.valor_devido.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          {client.telefone || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          {client.email || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'relatorios' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-yellow-400">
              <h3 className="text-lg font-medium text-yellow-400 mb-4">📊 Relatórios Detalhados</h3>
              
              {/* Resumo Anual */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">
                    R$ {monthlyData.reduce((acc, item) => acc + item.total_entradas, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-sm text-gray-300">Total Entradas</div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-red-400">
                    R$ {monthlyData.reduce((acc, item) => acc + item.total_saidas, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-sm text-gray-300">Total Saídas</div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-400">
                    R$ {monthlyData.reduce((acc, item) => acc + item.faturamento_liquido, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-sm text-gray-300">Lucro Líquido</div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-400">
                    {monthlyData.reduce((acc, item) => acc + item.transacoes_count, 0)}
                  </div>
                  <div className="text-sm text-gray-300">Total Transações</div>
                </div>
              </div>

              {/* Tabela Detalhada por Mês */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Mês
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Entradas
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Saídas
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Lucro Líquido
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Transações
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        Margem (%)
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-gray-800 divide-y divide-gray-700">
                    {monthlyData.map((month) => {
                      const margem = month.total_entradas > 0 ? ((month.faturamento_liquido / month.total_entradas) * 100) : 0;
                      return (
                        <tr key={month.mes} className="hover:bg-gray-700">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-yellow-400">
                            {month.nome_mes}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400">
                            R$ {month.total_entradas.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-red-400">
                            R$ {month.total_saidas.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${month.faturamento_liquido >= 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                            R$ {month.faturamento_liquido.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {month.transacoes_count}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm ${margem >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {margem.toFixed(1)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;