// State variables
let fundsData = [];
let filteredData = [];
let selectedFund = null;
let navChartInstance = null;
let currentSortKey = 'name';
let currentSortAsc = true;

// DOM Elements
const tableBody = document.getElementById('funds-table-body');
const searchInput = document.getElementById('search-fund');
const categoryFilter = document.getElementById('filter-category');
const amcFilter = document.getElementById('filter-amc');
const expenseFilter = document.getElementById('filter-expense');
const visibleCountBadge = document.getElementById('visible-funds-count');
const lastUpdatedElement = document.getElementById('last-updated-date');

// Stats DOM Elements
const statTotalFunds = document.getElementById('stat-total-funds');
const statTotalAum = document.getElementById('stat-total-aum');

// Detail Panel DOM Elements
const detailCardEmpty = document.getElementById('detail-card-empty');
const detailCardMain = document.getElementById('detail-card-main');
const detailName = document.getElementById('detail-name');
const detailBenchmark = document.getElementById('detail-benchmark');
const detailExpense = document.getElementById('detail-expense');
const detailAum = document.getElementById('detail-aum');
const detailTrackingError = document.getElementById('detail-tracking-error');
const detailLatestNav = document.getElementById('detail-latest-nav');
const detailChartLoading = document.getElementById('chart-loading');

const detailRet6M = document.getElementById('detail-ret-6M');
const detailRet1Y = document.getElementById('detail-ret-1Y');
const detailRet2Y = document.getElementById('detail-ret-2Y');
const detailRet3Y = document.getElementById('detail-ret-3Y');
const detailRet5Y = document.getElementById('detail-ret-5Y');

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadFundsData();
    setupEventListeners();
});

// Load Compiled Data
async function loadFundsData() {
    try {
        const response = await fetch('funds_data.json');
        if (!response.ok) {
            throw new Error('Failed to fetch funds data');
        }
        fundsData = await response.json();
        filteredData = [...fundsData];
        
        populateAmcFilter();
        updateStats();
        renderTable();
        
        if (fundsData.length > 0) {
            lastUpdatedElement.textContent = `Last Updated: ${fundsData[0].latest_date}`;
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 3rem; color: var(--danger);">
                    <i class="fa-solid fa-triangle-exclamation" style="margin-right: 8px;"></i>
                    Failed to load funds data. Make sure compile_data.py has run successfully.
                </td>
            </tr>
        `;
    }
}

// Setup Interaction Handlers
function setupEventListeners() {
    searchInput.addEventListener('input', applyFilters);
    categoryFilter.addEventListener('change', applyFilters);
    amcFilter.addEventListener('change', applyFilters);
    expenseFilter.addEventListener('change', applyFilters);
    
    // Table Sorting headers click
    document.querySelectorAll('.funds-table th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const key = th.getAttribute('data-sort');
            handleSort(key);
        });
    });
}

// Calculate Dashboard KPI Summaries
function updateStats() {
    if (fundsData.length === 0) return;
    
    // Total number of funds
    statTotalFunds.textContent = fundsData.length;
    
    // Total AUM in Crores
    const totalAumVal = fundsData.reduce((acc, curr) => acc + (curr.aum || 0), 0);
    if (totalAumVal >= 1000) {
        statTotalAum.textContent = `₹${(totalAumVal / 1000).toFixed(2)}K Cr`;
    } else {
        statTotalAum.textContent = `₹${totalAumVal.toLocaleString('en-IN')} Cr`;
    }
}

// Filter and Sort Data
function applyFilters() {
    const query = searchInput.value.toLowerCase().trim();
    const category = categoryFilter.value;
    const amc = amcFilter.value;
    const expenseTier = expenseFilter.value;
    
    filteredData = fundsData.filter(fund => {
        // Text search
        const matchesQuery = fund.name.toLowerCase().includes(query) || 
                             fund.fund_house.toLowerCase().includes(query) ||
                             fund.benchmark.toLowerCase().includes(query);
                             
        // Category filter
        const matchesCategory = category === 'all' || fund.category === category;
        
        // AMC filter
        const matchesAmc = amc === 'all' || fund.fund_house === amc;
        
        // Expense tier filter
        let matchesExpense = true;
        if (expenseTier === 'low') {
            matchesExpense = fund.expense_ratio !== null && fund.expense_ratio < 0.15;
        } else if (expenseTier === 'mid') {
            matchesExpense = fund.expense_ratio !== null && fund.expense_ratio >= 0.15 && fund.expense_ratio <= 0.30;
        } else if (expenseTier === 'high') {
            matchesExpense = fund.expense_ratio !== null && fund.expense_ratio > 0.30;
        }
        
        return matchesQuery && matchesCategory && matchesAmc && matchesExpense;
    });
    
    // Re-apply sorting to the filtered subset
    sortData(currentSortKey, currentSortAsc);
    renderTable();
}

// Handle Sorting State Changes
function handleSort(key) {
    if (currentSortKey === key) {
        currentSortAsc = !currentSortAsc;
    } else {
        currentSortKey = key;
        currentSortAsc = true;
    }
    
    // Update visual sorted markers in headers
    document.querySelectorAll('.funds-table th').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
    });
    
    const activeHeader = document.querySelector(`.funds-table th[data-sort="${key}"]`);
    if (activeHeader) {
        activeHeader.classList.add(currentSortAsc ? 'sorted-asc' : 'sorted-desc');
    }
    
    sortData(currentSortKey, currentSortAsc);
    renderTable();
}

// Sort Array in Memory
function sortData(key, asc) {
    const dir = asc ? 1 : -1;
    
    filteredData.sort((a, b) => {
        let valA, valB;
        
        // Map sort keys to object properties
        if (key === 'name') {
            valA = a.name;
            valB = b.name;
        } else if (key === 'category') {
            valA = a.category;
            valB = b.category;
        } else if (key === 'expense') {
            valA = a.expense_ratio;
            valB = b.expense_ratio;
        } else if (key === 'aum') {
            valA = a.aum;
            valB = b.aum;
        } else if (key === 'tracking_error') {
            valA = a.tracking_error;
            valB = b.tracking_error;
        } else if (key.startsWith('return_')) {
            const period = key.split('_')[1];
            valA = a.returns[period];
            valB = b.returns[period];
        }
        
        // Handle Null values: always push nulls to the bottom regardless of sort order
        if (valA === undefined || valA === null) return 1;
        if (valB === undefined || valB === null) return -1;
        
        if (typeof valA === 'string') {
            return dir * valA.localeCompare(valB);
        } else {
            return dir * (valA - valB);
        }
    });
}

// Render Comparison Grid Rows
function renderTable() {
    tableBody.innerHTML = '';
    visibleCountBadge.textContent = `${filteredData.length} Funds`;
    
    if (filteredData.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                    <i class="fa-solid fa-magnifying-glass" style="margin-right: 8px;"></i>
                    No index funds match your filter criteria.
                </td>
            </tr>
        `;
        return;
    }
    
    filteredData.forEach(fund => {
        const row = document.createElement('tr');
        if (selectedFund && selectedFund.scheme_code === fund.scheme_code) {
            row.classList.add('selected');
        }
        
        row.addEventListener('click', () => {
            selectFund(fund, row);
        });
        
        // Format returns cells with color badges
        const r6M = formatReturnBadge(fund.returns['6M']);
        const r1Y = formatReturnBadge(fund.returns['1Y']);
        const r3Y = formatReturnBadge(fund.returns['3Y']);
        const r5Y = formatReturnBadge(fund.returns['5Y']);
        
        row.innerHTML = `
            <td>
                <div class="fund-name-cell" title="${fund.name}">${fund.name}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 2px;">AMFI: ${fund.scheme_code}</div>
            </td>
            <td><span class="fund-category-cell">${getShortCategory(fund.category)}</span></td>
            <td class="text-number">${fund.expense_ratio !== null ? fund.expense_ratio.toFixed(2) + '%' : '-'}</td>
            <td class="text-number">${fund.aum !== null ? fund.aum.toLocaleString('en-IN') : '-'}</td>
            <td class="text-number">${fund.tracking_error !== null ? fund.tracking_error.toFixed(2) + '%' : '-'}</td>
            <td>${r6M}</td>
            <td>${r1Y}</td>
            <td>${r3Y}</td>
            <td>${r5Y}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

function getShortCategory(cat) {
    // Returns a shorter category label for table display spacing
    if (cat.includes('Nifty 50)')) return 'Nifty 50';
    if (cat.includes('Nifty Next 50)')) return 'Next 50';
    if (cat.includes('Midcap 150)')) return 'Mid 150';
    if (cat.includes('Smallcap 250)')) return 'Small 250';
    return cat;
}

function formatReturnBadge(val) {
    if (val === null || val === undefined) return '<span class="badge badge-neutral">-</span>';
    const num = parseFloat(val);
    const sign = num > 0 ? '+' : '';
    if (num > 12) {
        return `<span class="badge badge-green">${sign}${num.toFixed(1)}%</span>`;
    } else if (num >= 0) {
        return `<span class="badge badge-orange">${sign}${num.toFixed(1)}%</span>`;
    } else {
        return `<span class="badge badge-red">${num.toFixed(1)}%</span>`;
    }
}

// Select a Fund and Load Details
function selectFund(fund, rowElement) {
    selectedFund = fund;
    
    // Highlight table row
    document.querySelectorAll('#funds-table-body tr').forEach(r => r.classList.remove('selected'));
    rowElement.classList.add('selected');
    
    // Update main detail panel UI
    detailCardEmpty.classList.add('hidden');
    detailCardMain.classList.remove('hidden');
    
    detailName.textContent = fund.name;
    detailBenchmark.textContent = fund.benchmark;
    
    detailExpense.textContent = fund.expense_ratio !== null ? `${fund.expense_ratio.toFixed(2)}%` : 'N/A';
    detailAum.textContent = fund.aum !== null ? `₹${fund.aum.toLocaleString('en-IN')} Cr` : 'N/A';
    detailTrackingError.textContent = fund.tracking_error !== null ? `${fund.tracking_error.toFixed(2)}%` : 'N/A';
    detailLatestNav.textContent = `₹${fund.latest_nav.toFixed(4)}`;
    
    // Update timeline values with styling
    updateDetailReturnCell(detailRet6M, fund.returns['6M']);
    updateDetailReturnCell(detailRet1Y, fund.returns['1Y']);
    updateDetailReturnCell(detailRet2Y, fund.returns['2Y']);
    updateDetailReturnCell(detailRet3Y, fund.returns['3Y']);
    updateDetailReturnCell(detailRet5Y, fund.returns['5Y']);
    
    // Load historical NAV chart
    fetchAndRenderChart(fund.scheme_code, fund.name);
}

function updateDetailReturnCell(element, val) {
    element.className = 'timeline-node-val text-number';
    if (val === null || val === undefined) {
        element.textContent = '-';
        element.classList.add('badge-neutral');
    } else {
        const num = parseFloat(val);
        const sign = num > 0 ? '+' : '';
        element.textContent = `${sign}${num.toFixed(2)}%`;
        if (num > 0) {
            element.classList.add('pos-value');
        } else if (num < 0) {
            element.classList.add('neg-value');
        }
    }
}

// Fetch Historical NAV from API and Plot Chart
async function fetchAndRenderChart(schemeCode, fundName) {
    detailChartLoading.classList.remove('hidden');
    
    try {
        const response = await fetch(`https://api.mfapi.in/mf/${schemeCode}`);
        if (!response.ok) {
            throw new Error('Failed to load live chart history');
        }
        
        const data = await response.json();
        let navData = data.data || [];
        
        if (navData.length === 0) {
            throw new Error('No historical data found');
        }
        
        // The API returns newest data first. We need oldest data first for chronological chart plotting.
        navData = [...navData].reverse();
        
        // Downsample NAV data points to keep Chart.js rendering extremely fast and clean
        // We target ~150-200 chart points max.
        const targetPoints = 180;
        let chartDataPoints = [];
        
        if (navData.length <= targetPoints) {
            chartDataPoints = navData;
        } else {
            const step = Math.ceil(navData.length / targetPoints);
            for (let i = 0; i < navData.length; i += step) {
                chartDataPoints.push(navData[i]);
            }
            // Always push the absolute latest data point to keep it correct
            if (chartDataPoints[chartDataPoints.length - 1].date !== navData[navData.length - 1].date) {
                chartDataPoints.push(navData[navData.length - 1]);
            }
        }
        
        const labels = chartDataPoints.map(d => d.date);
        const navValues = chartDataPoints.map(d => parseFloat(d.nav));
        
        renderChart(labels, navValues, fundName);
    } catch (error) {
        console.error('Error drawing chart:', error);
        // Fallback: draw an empty chart with an error message
        renderChart([], [], 'Failed to load historical data');
    } finally {
        detailChartLoading.classList.add('hidden');
    }
}

// Render Chart.js Chart
function renderChart(labels, dataValues, datasetLabel) {
    if (navChartInstance) {
        navChartInstance.destroy();
    }
    
    const ctx = document.getElementById('nav-chart').getContext('2d');
    
    // Gradient background for the line chart fill
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.35)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.00)');
    
    navChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Net Asset Value (NAV)',
                data: dataValues,
                borderColor: '#6366f1',
                borderWidth: 2,
                pointBackgroundColor: '#06b6d4',
                pointBorderColor: '#0f1016',
                pointBorderWidth: 1,
                pointRadius: (context) => {
                    // Show dots only on hover or for the final/first points to look sleek
                    const index = context.dataIndex;
                    const count = context.dataset.data.length;
                    return (index === 0 || index === count - 1) ? 4 : 0;
                },
                pointHoverRadius: 6,
                fill: true,
                backgroundColor: gradient,
                tension: 0.15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(15, 16, 22, 0.95)',
                    titleColor: '#f3f4f6',
                    bodyColor: '#e5e7eb',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 10,
                    titleFont: {
                        family: 'Plus Jakarta Sans',
                        weight: 'bold'
                    },
                    bodyFont: {
                        family: 'Plus Jakarta Sans'
                    },
                    callbacks: {
                        label: function(context) {
                            return `NAV: ₹${context.raw.toFixed(4)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Plus Jakarta Sans',
                            size: 9
                        },
                        maxTicksLimit: 6
                    },
                    border: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)'
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Plus Jakarta Sans',
                            size: 10
                        },
                        callback: function(value) {
                            return '₹' + value.toFixed(1);
                        }
                    },
                    border: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            }
        }
    });
}

// Populate AMC Dropdown dynamically from JSON
function populateAmcFilter() {
    const amcs = [...new Set(fundsData.map(f => f.fund_house).filter(Boolean))];
    amcs.sort((a, b) => a.localeCompare(b));
    
    amcFilter.innerHTML = '<option value="all">All AMCs</option>';
    
    amcs.forEach(amc => {
        const option = document.createElement('option');
        option.value = amc;
        option.textContent = amc;
        amcFilter.appendChild(option);
    });
}
