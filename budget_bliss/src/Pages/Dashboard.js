import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './Styles/Dashboard.css';

function Dashboard() {
  const [data, setData] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      const accessTokenString = localStorage.getItem('access_token');
      if (!accessTokenString) {
        setLoading(false);
        return;
      }

      try {
        const accessToken = JSON.parse(accessTokenString);
        
        // Fetch user info
        const userInfoResponse = await axios.get('/api/user_info', {
          headers: { Authorization: `Bearer ${JSON.stringify(accessToken)}` }
        });
        setUserInfo(userInfoResponse.data);

        // Fetch and process data
        await axios.post('/api/fetch_data', { access_token: accessToken });
        await axios.post('/api/process_expenses', { access_token: accessToken });
        
        // Get results for the specific user
        const results = await axios.get(`/api/get_results?user_id=${userInfoResponse.data.id}`);
        setData(results.data);
      } catch (error) {
        console.error('Error:', error.response ? error.response.data : error.message);
        setError('An error occurred. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const formatINR = (amount) => {
    return isNaN(amount) || amount === null
      ? 'N/A'
      : new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }).format(amount);
  };

  // Compute summary statistics from data
  const summaryStats = useMemo(() => {
    if (!data) return null;

    try {
      const predictions = JSON.parse(data.predictions);
      const expenseSums = JSON.parse(data.expense_sums);

      const totalExpenses = predictions.length;

      const totalPaid = expenseSums.reduce(
        (sum, item) => sum + (parseFloat(item['Paid Amount']) || 0), 0
      );

      const totalOwed = expenseSums.reduce(
        (sum, item) => sum + (parseFloat(item['Owed Amount']) || 0), 0
      );

      const topCategory = expenseSums.length > 0
        ? expenseSums.reduce((max, item) =>
            (parseFloat(item['Paid Amount']) || 0) > (parseFloat(max['Paid Amount']) || 0) ? item : max
          ).predicted_expense_type
        : 'N/A';

      const categoriesCount = expenseSums.length;

      return { totalExpenses, totalPaid, totalOwed, topCategory, categoriesCount };
    } catch {
      return null;
    }
  }, [data]);

  if (loading) return <div className="dashboard-loading">Loading...</div>;
  if (error) return <div className="dashboard-error">Error: {error}</div>;
  if (!localStorage.getItem('access_token')) {
    return (
      <div className="dashboard-login-prompt">
        <h2>Please log in to view your dashboard</h2>
        <Link to="/login" className="dashboard-login-button">Log In</Link>
      </div>
    );
  }
  if (!data) return <div className="dashboard-no-data">No data available</div>;

  const predictions = JSON.parse(data.predictions);
  const expenseSums = JSON.parse(data.expense_sums);

  const nonPaymentPredictions = predictions.filter((p) => {
    const desc = p.description || p.Description || '';
    return desc && !['payment', 'settle all balances'].includes(desc.toLowerCase());
  });
  const displayedPredictions = nonPaymentPredictions.slice(0, 10);

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">Your Splitwise Dashboard</h1>
      {userInfo && <p className="dashboard-welcome">Welcome, {userInfo.name}!</p>}

      {/* Summary Statistics Cards */}
      {summaryStats && (
        <section className="dashboard-stats-grid">
          <div className="stat-card">
            <span className="stat-label">Total Expenses</span>
            <span className="stat-value">{summaryStats.totalExpenses}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Paid</span>
            <span className="stat-value">{formatINR(summaryStats.totalPaid)}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Owed</span>
            <span className="stat-value">{formatINR(summaryStats.totalOwed)}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Top Category</span>
            <span className="stat-value">{summaryStats.topCategory}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Categories</span>
            <span className="stat-value">{summaryStats.categoriesCount}</span>
          </div>
        </section>
      )}

      <section className="dashboard-section">
        <h2>Recent Expense Predictions</h2>
        <div className="dashboard-table-container">
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Description</th>
                <th>Cost</th>
                <th>Predicted Type</th>
              </tr>
            </thead>
            <tbody>
              {displayedPredictions.map((prediction, index) => {
                const desc = prediction.description || prediction.Description || 'Unknown';
                const cost = prediction.total_cost || prediction.Cost || prediction.amount || 0;
                return (
                  <tr key={index}>
                    <td>{desc}</td>
                    <td>{formatINR(parseFloat(cost))}</td>
                    <td>{prediction.predicted_expense_type}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="dashboard-section">
        <h2>Expense Sums by Category</h2>
        <div className="dashboard-table-container">
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Paid Amount</th>
                <th>Owed Amount</th>
              </tr>
            </thead>
            <tbody>
              {expenseSums.map((sum, index) => (
                <tr key={index}>
                  <td>{sum.predicted_expense_type || 'Unknown'}</td>
                  <td>{formatINR(parseFloat(sum['Paid Amount']))}</td>
                  <td>{formatINR(parseFloat(sum['Owed Amount']))}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;