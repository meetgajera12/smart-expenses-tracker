// Backend API base URL
// Tip: To point to your Render backend in production, update this URL or set localStorage.setItem("API_URL", "https://your-backend.onrender.com")
const API_URL = localStorage.getItem("API_URL") || window.API_URL || "http://127.0.0.1:8000";


// Chart instances
let categoryChartInstance = null;
let dailyChartInstance = null;

// Stored expenses list for client-side filtering
let allExpenses = [];

// ==========================================
// 1. INITIALIZATION & TAB SWITCHING
// ==========================================
document.addEventListener("DOMContentLoaded", function () {
    // Set default date input to today
    const today = new Date().toISOString().split("T")[0];
    const expDateInput = document.getElementById("exp-date");
    if (expDateInput) {
        expDateInput.value = today;
    }

    // Load initial dashboard and expenses
    loadDashboard();
    loadExpenses();
});

// Simple function to switch visible tabs
function showTab(tabId) {
    // Hide all tabs
    const tabs = document.querySelectorAll(".tab-content");
    tabs.forEach(tab => tab.classList.remove("active"));

    // Deactivate all nav buttons
    const navButtons = document.querySelectorAll(".app-nav-tab");
    navButtons.forEach(btn => btn.classList.remove("active"));

    // Activate selected tab
    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.classList.add("active");
    }

    // Highlight clicked button
    const activeBtn = Array.from(navButtons).find(btn => 
        btn.getAttribute("onclick") && btn.getAttribute("onclick").includes(tabId)
    );
    if (activeBtn) {
        activeBtn.classList.add("active");
    }

    // If navigating to Dashboard or Expenses, reload fresh data
    if (tabId === "dashboard-tab") {
        loadDashboard();
    } else if (tabId === "list-tab") {
        loadExpenses();
    }
}


// ==========================================
// 2. DASHBOARD & CHARTS (WITH FILTERS)
// ==========================================
async function loadDashboard() {
    const monthInput = document.getElementById("dash-month") ? document.getElementById("dash-month").value.trim() : "";
    const categoryInput = document.getElementById("dash-category") ? document.getElementById("dash-category").value : "";
    const paymentInput = document.getElementById("dash-payment") ? document.getElementById("dash-payment").value : "";

    let queryParams = [];
    if (monthInput && monthInput !== "all") {
        queryParams.push("month=" + encodeURIComponent(monthInput));
    }
    if (categoryInput) {
        queryParams.push("category=" + encodeURIComponent(categoryInput));
    }
    if (paymentInput) {
        queryParams.push("payment_method=" + encodeURIComponent(paymentInput));
    }

    let url = API_URL + "/dashboard";
    if (queryParams.length > 0) {
        url += "?" + queryParams.join("&");
    }

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error("Failed to load dashboard data");
        }

        const data = await response.json();

        // 1. Update metric cards
        document.getElementById("stat-total-spending").innerText = "₹" + data.total_amount.toFixed(2);
        document.getElementById("stat-total-count").innerText = data.total_expenses;
        document.getElementById("stat-budget-amount").innerText = "₹" + data.budget.amount.toFixed(2);
        document.getElementById("stat-budget-remaining").innerText = "₹" + data.budget.remaining.toFixed(2);

        // 2. Update budget card
        updateBudgetUI(data.budget);

        // 3. Update charts
        renderCategoryChart(data.category_chart.labels, data.category_chart.values);
        renderDailyChart(data.daily_chart.dates, data.daily_chart.amounts);

        // 4. Update AI Insights
        const insightsList = document.getElementById("insights-list");
        insightsList.innerHTML = "";
        data.insights.forEach(item => {
            const li = document.createElement("li");
            li.innerHTML = '<span class="material-symbols-outlined color-blue" style="font-size:18px;">auto_awesome</span> ' + item;
            insightsList.appendChild(li);
        });

        // 5. Update ML Forecast
        document.getElementById("forecast-daily").innerText = "₹" + data.forecast.average_spending_per_active_day.toFixed(2) + " / day";
        const forecast7El = document.getElementById("forecast-7day");
        if (forecast7El && data.forecast.next_7_days_spending !== undefined) {
            forecast7El.innerText = "₹" + data.forecast.next_7_days_spending.toFixed(2);
        }
        document.getElementById("forecast-30day").innerText = "₹" + data.forecast.forecasted_30_day_spending.toFixed(2);
        document.getElementById("forecast-message").innerText = data.forecast.message;

        // 6. Update Recurring Expenses
        const recurringContainer = document.getElementById("recurring-expenses-container");
        if (recurringContainer) {
            recurringContainer.innerHTML = "";
            const recurringList = data.recurring_expenses || [];
            if (recurringList.length === 0) {
                recurringContainer.innerHTML = '<p class="text-subtle">No recurring subscriptions or bills detected.</p>';
            } else {
                recurringList.forEach(item => {
                    const pill = document.createElement("div");
                    pill.style.cssText = "background: var(--surface-variant); border: 1px solid var(--border-default); padding: 0.65rem 1.1rem; border-radius: 12px; display: flex; align-items: center; gap: 0.75rem;";
                    pill.innerHTML = `
                        <span class="material-symbols-outlined color-blue" style="font-size: 22px;">autorenew</span>
                        <div>
                            <strong style="color: var(--text-primary); font-size: 0.95rem;">${item.merchant}</strong>
                            <div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 2px;">
                                ₹${Number(item.amount).toLocaleString()} • <span class="app-badge app-badge-cat">${item.frequency}</span>
                            </div>
                        </div>
                    `;
                    recurringContainer.appendChild(pill);
                });
            }
        }

        // Set backend status to connected
        const statusEl = document.getElementById("backend-status");
        if (statusEl) {
            statusEl.innerHTML = '<span class="pulse-dot"></span><span>Connected</span>';
            statusEl.style.backgroundColor = "var(--color-green-tint)";
            statusEl.style.color = "var(--color-green)";
        }

    } catch (error) {
        console.error("Dashboard error:", error);
        const statusEl = document.getElementById("backend-status");
        if (statusEl) {
            statusEl.innerHTML = '<span class="pulse-dot" style="background-color: var(--color-red); box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);"></span><span>Offline</span>';
            statusEl.style.backgroundColor = "var(--color-red-tint)";
            statusEl.style.color = "var(--color-red)";
        }
    }
}

function setDashboardPreset(month, category, payment) {
    const monthEl = document.getElementById("dash-month");
    const catEl = document.getElementById("dash-category");
    const payEl = document.getElementById("dash-payment");

    if (monthEl) monthEl.value = (month === "all") ? "" : month;
    if (catEl) catEl.value = category;
    if (payEl) payEl.value = payment;

    // Update active preset button highlight
    const chips = document.querySelectorAll(".preset-chips-row .app-chip");
    chips.forEach(c => c.classList.remove("active"));
    if (event && event.currentTarget) {
        event.currentTarget.classList.add("active");
    }

    loadDashboard();
}

function clearDashboardFilters() {
    const monthEl = document.getElementById("dash-month");
    const catEl = document.getElementById("dash-category");
    const payEl = document.getElementById("dash-payment");

    if (monthEl) monthEl.value = "";
    if (catEl) catEl.value = "";
    if (payEl) payEl.value = "";

    const chips = document.querySelectorAll(".preset-chips-row .app-chip");
    chips.forEach(c => c.classList.remove("active"));

    loadDashboard();
}

function updateBudgetUI(budget) {
    const statusText = document.getElementById("budget-status-text");
    const progressBar = document.getElementById("budget-progress-bar");
    const spentLabel = document.getElementById("budget-spent-label");
    const percentLabel = document.getElementById("budget-percent-label");

    // Populate the budget inputs
    document.getElementById("budget-input").value = budget.amount;
    if (budget.month) {
        document.getElementById("budget-month-input").value = budget.month;
    }

    statusText.innerText = `Status: ${budget.status} (${budget.month || 'All Months'})`;
    spentLabel.innerText = `Spent: ₹${budget.spent.toFixed(2)} of ₹${budget.amount.toFixed(2)}`;
    percentLabel.innerText = `${budget.percentage_used}% used`;

    // Progress bar width & color coding
    let percent = Math.min(budget.percentage_used, 100);
    progressBar.style.width = percent + "%";

    if (budget.percentage_used > 100) {
        progressBar.style.backgroundColor = "var(--color-red)";
    } else if (budget.percentage_used >= 80) {
        progressBar.style.backgroundColor = "var(--color-yellow)";
    } else {
        progressBar.style.backgroundColor = "var(--color-primary)";
    }
}

async function saveBudget(event) {
    event.preventDefault();

    const amount = parseFloat(document.getElementById("budget-input").value);
    const month = document.getElementById("budget-month-input").value.trim();

    try {
        const response = await fetch(API_URL + "/budget", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount: amount, month: month })
        });

        if (response.ok) {
            showToast("Budget updated successfully!");
            loadDashboard();
        } else {
            showToast("Failed to save budget", true);
        }
    } catch (err) {
        showToast("Error connecting to server", true);
    }
}

function renderCategoryChart(labels, values) {
    const ctx = document.getElementById("categoryChart").getContext("2d");

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    // Modern Vibrant Palette
    categoryChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    "#2563eb", "#10b981", "#f59e0b", "#ef4444", 
                    "#8b5cf6", "#06b6d4", "#f97316", "#64748b"
                ],
                borderWidth: 2,
                borderColor: "#ffffff"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: { 
                        color: "#475569",
                        font: { family: "'Inter', sans-serif" }
                    }
                }
            }
        }
    });
}

function renderDailyChart(dates, amounts) {
    const ctx = document.getElementById("dailyChart").getContext("2d");

    if (dailyChartInstance) {
        dailyChartInstance.destroy();
    }

    dailyChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: dates,
            datasets: [{
                label: "Daily Spend (₹)",
                data: amounts,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37, 99, 235, 0.12)",
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: "#2563eb"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { 
                    ticks: { color: "#64748b", font: { family: "'Inter', sans-serif" } }, 
                    grid: { color: "rgba(0,0,0,0.05)" } 
                },
                y: { 
                    ticks: { color: "#64748b", font: { family: "'Inter', sans-serif" } }, 
                    grid: { color: "rgba(0,0,0,0.05)" } 
                }
            },
            plugins: {
                legend: { 
                    labels: { color: "#475569", font: { family: "'Inter', sans-serif" } } 
                }
            }
        }
    });
}


// ==========================================
// 3. ADD EXPENSE (WITH ML PREDICTION)
// ==========================================
async function handleAddExpense(event) {
    event.preventDefault();

    const description = document.getElementById("exp-description").value.trim();
    const amount = parseFloat(document.getElementById("exp-amount").value);
    const date = document.getElementById("exp-date").value;
    const payment_method = document.getElementById("exp-payment").value;

    const payload = {
        description: description,
        amount: amount,
        date: date,
        payment_method: payment_method
    };

    const resultBox = document.getElementById("add-result-box");
    resultBox.classList.add("hidden");

    try {
        const response = await fetch(API_URL + "/expenses", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const added = await response.json();

            // Display predicted ML Category and Confidence
            resultBox.innerHTML = `
                <h3 style="color: var(--color-green); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span class="material-symbols-outlined">check_circle</span> Expense Added Successfully!
                </h3>
                <p style="margin-bottom: 0.3rem;"><strong>Predicted Category:</strong> <span class="app-badge app-badge-cat">${added.category}</span></p>
                <p style="margin-bottom: 0.3rem;"><strong>ML Confidence:</strong> ${added.confidence !== null ? (added.confidence * 100).toFixed(1) + '%' : 'N/A'}</p>
                <p><strong>Amount:</strong> ₹${added.amount} | <strong>Payment:</strong> ${added.payment_method}</p>
            `;
            resultBox.classList.remove("hidden");

            // Reset form inputs
            document.getElementById("exp-description").value = "";
            document.getElementById("exp-amount").value = "";

            showToast("Expense added and categorized by ML!");
        } else {
            const errText = await response.text();
            showToast("Error adding expense: " + errText, true);
        }
    } catch (err) {
        showToast("Error connecting to backend", true);
    }
}


// ==========================================
// 4. BILL PHOTO AI (OCR & RAG)
// ==========================================
function previewBillImage(event) {
    const file = event.target.files[0];
    const previewContainer = document.getElementById("image-preview-container");
    const previewImg = document.getElementById("bill-preview-img");

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            previewImg.src = e.target.result;
            previewContainer.classList.remove("hidden");
        };
        reader.readAsDataURL(file);
    } else {
        previewContainer.classList.add("hidden");
    }
}

async function handleBillUpload(event) {
    event.preventDefault();

    const fileInput = document.getElementById("bill-file");
    const questionInput = document.getElementById("bill-question");
    const loader = document.getElementById("bill-loader");
    const resultBox = document.getElementById("bill-result-box");

    if (!fileInput.files || fileInput.files.length === 0) {
        showToast("Please select a bill image", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const question = questionInput.value.trim();
    let url = API_URL + "/expenses/bill-photo";
    if (question) {
        url += "?question=" + encodeURIComponent(question);
    }

    loader.classList.remove("hidden");
    resultBox.classList.add("hidden");

    try {
        const response = await fetch(url, {
            method: "POST",
            body: formData
        });

        loader.classList.add("hidden");

        if (response.ok) {
            const result = await response.json();
            const bill = result.bill;
            const expense = result.expense;

            let itemsHtml = "";
            if (bill.items && bill.items.length > 0) {
                itemsHtml = "<h4 style='margin: 0.5rem 0;'>Items Detected:</h4><ul style='padding-left: 1.2rem;'>" + 
                    bill.items.map(item => `<li>${item.name}</li>`).join("") + 
                    "</ul>";
            }

            let ragHtml = "";
            if (result.rag_answer) {
                ragHtml = `
                    <div style="margin-top: 1rem; padding: 0.85rem; background: var(--color-blue-tint); border-left: 3px solid var(--color-primary); border-radius: 6px;">
                        <strong style="color: var(--color-primary);">AI Answer to "${result.rag_question}":</strong>
                        <p style="margin-top: 0.3rem; color: var(--text-primary);">${result.rag_answer}</p>
                    </div>
                `;
            }

            resultBox.innerHTML = `
                <h3 style="color: var(--color-green); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span class="material-symbols-outlined">receipt_long</span> Bill Processed & Saved!
                </h3>
                <p><strong>Merchant:</strong> ${bill.merchant || "N/A"}</p>
                <p><strong>Amount:</strong> ₹${bill.amount}</p>
                <p><strong>Date:</strong> ${bill.date || "N/A"}</p>
                <p><strong>Predicted Category:</strong> <span class="app-badge app-badge-cat">${expense.category}</span></p>
                ${itemsHtml}
                ${ragHtml}
            `;
            resultBox.classList.remove("hidden");
            showToast("Bill successfully scanned and saved!");
        } else {
            const err = await response.text();
            showToast("Error processing bill: " + err, true);
        }
    } catch (error) {
        loader.classList.add("hidden");
        showToast("Error uploading bill", true);
    }
}


// ==========================================
// 5. ALL EXPENSES LIST & FILTERS
// ==========================================
async function loadExpenses() {
    try {
        const response = await fetch(API_URL + "/expenses");
        if (!response.ok) throw new Error("Failed to fetch expenses");

        const data = await response.json();
        allExpenses = data.expenses || [];

        populateCategoryFilter(allExpenses);
        renderExpensesTable(allExpenses);
    } catch (err) {
        console.error("Error loading expenses:", err);
    }
}

function populateCategoryFilter(expenses) {
    const categorySelect = document.getElementById("filter-category");
    const currentVal = categorySelect.value;

    const categories = Array.from(new Set(expenses.map(e => e.category).filter(Boolean)));
    
    categorySelect.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(cat => {
        const opt = document.createElement("option");
        opt.value = cat;
        opt.innerText = cat;
        categorySelect.appendChild(opt);
    });

    categorySelect.value = currentVal;
}

function filterExpenses() {
    const keyword = document.getElementById("search-keyword") ? document.getElementById("search-keyword").value.toLowerCase().trim() : "";
    const category = document.getElementById("filter-category") ? document.getElementById("filter-category").value.toLowerCase() : "";
    const payment = document.getElementById("filter-payment") ? document.getElementById("filter-payment").value.toLowerCase() : "";
    
    const minAmount = document.getElementById("filter-min-amount") && document.getElementById("filter-min-amount").value ? parseFloat(document.getElementById("filter-min-amount").value) : 0;
    const maxAmount = document.getElementById("filter-max-amount") && document.getElementById("filter-max-amount").value ? parseFloat(document.getElementById("filter-max-amount").value) : 0;
    
    const fromDate = document.getElementById("filter-from-date") ? document.getElementById("filter-from-date").value : "";
    const toDate = document.getElementById("filter-to-date") ? document.getElementById("filter-to-date").value : "";
    
    const sortBy = document.getElementById("filter-sort") ? document.getElementById("filter-sort").value : "date-desc";

    let filtered = allExpenses.filter(item => {
        const itemDesc = item.description ? item.description.toLowerCase() : "";
        const itemCat = item.category ? item.category.toLowerCase() : "";
        const itemPay = item.payment_method ? item.payment_method.toLowerCase() : "";
        const itemDate = item.date || "";
        const itemAmount = parseFloat(item.amount) || 0;

        const matchKeyword = !keyword || itemDesc.includes(keyword) || itemCat.includes(keyword);
        const matchCategory = !category || itemCat === category;
        const matchPayment = !payment || itemPay === payment;
        const matchMin = minAmount <= 0 || itemAmount >= minAmount;
        const matchMax = maxAmount <= 0 || itemAmount <= maxAmount;
        const matchFromDate = !fromDate || itemDate >= fromDate;
        const matchToDate = !toDate || itemDate <= toDate;

        return matchKeyword && matchCategory && matchPayment && matchMin && matchMax && matchFromDate && matchToDate;
    });

    // Apply Sorting
    filtered.sort((a, b) => {
        if (sortBy === "date-desc") return (b.date || "").localeCompare(a.date || "");
        if (sortBy === "date-asc") return (a.date || "").localeCompare(b.date || "");
        if (sortBy === "amount-desc") return (parseFloat(b.amount) || 0) - (parseFloat(a.amount) || 0);
        if (sortBy === "amount-asc") return (parseFloat(a.amount) || 0) - (parseFloat(b.amount) || 0);
        return 0;
    });

    renderExpensesTable(filtered);
}

function resetExpensesFilters() {
    if (document.getElementById("search-keyword")) document.getElementById("search-keyword").value = "";
    if (document.getElementById("filter-category")) document.getElementById("filter-category").value = "";
    if (document.getElementById("filter-payment")) document.getElementById("filter-payment").value = "";
    if (document.getElementById("filter-min-amount")) document.getElementById("filter-min-amount").value = "";
    if (document.getElementById("filter-max-amount")) document.getElementById("filter-max-amount").value = "";
    if (document.getElementById("filter-from-date")) document.getElementById("filter-from-date").value = "";
    if (document.getElementById("filter-to-date")) document.getElementById("filter-to-date").value = "";
    if (document.getElementById("filter-sort")) document.getElementById("filter-sort").value = "date-desc";

    renderExpensesTable(allExpenses);
}

function renderExpensesTable(expenses) {
    const tbody = document.getElementById("expenses-table-body");
    tbody.innerHTML = "";

    if (!expenses || expenses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-subtle">No expenses found.</td></tr>`;
        return;
    }

    expenses.forEach((item, index) => {
        const tr = document.createElement("tr");

        const confidenceStr = item.confidence ? (item.confidence * 100).toFixed(0) + "%" : "-";

        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.date || "-"}</td>
            <td><strong>${item.description}</strong></td>
            <td><span class="app-badge app-badge-cat">${item.category || "Uncategorized"}</span></td>
            <td>${confidenceStr}</td>
            <td><span class="app-badge app-badge-pay">${item.payment_method || "Cash"}</span></td>
            <td><strong>₹${Number(item.amount).toFixed(2)}</strong></td>
            <td>
                <button class="app-btn app-btn-danger" onclick="deleteExpense(${item.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function deleteExpense(id) {
    if (!confirm("Are you sure you want to delete this expense?")) {
        return;
    }

    try {
        const response = await fetch(API_URL + "/expenses/" + id, {
            method: "DELETE"
        });

        if (response.ok) {
            showToast("Expense deleted successfully");
            loadExpenses();
            loadDashboard();
        } else {
            showToast("Failed to delete expense", true);
        }
    } catch (err) {
        showToast("Error connecting to server", true);
    }
}


// ==========================================
// 6. AI EXPENSE ASSISTANT
// ==========================================
function askPredefined(question) {
    document.getElementById("ai-question").value = question;
    document.getElementById("ai-assistant-form").dispatchEvent(new Event("submit"));
}

async function handleAiAssistant(event) {
    event.preventDefault();

    const questionInput = document.getElementById("ai-question");
    const question = questionInput.value.trim();
    if (!question) return;

    const loader = document.getElementById("ai-loader");
    const answerBox = document.getElementById("ai-answer-box");
    const answerText = document.getElementById("ai-answer-text");

    loader.classList.remove("hidden");
    answerBox.classList.add("hidden");

    try {
        const response = await fetch(API_URL + "/aiassistant?que=" + encodeURIComponent(question), {
            method: "POST"
        });

        loader.classList.add("hidden");

        if (response.ok) {
            const answer = await response.json();
            answerText.innerText = answer;
            answerBox.classList.remove("hidden");
        } else {
            const err = await response.text();
            showToast("AI Assistant error: " + err, true);
        }
    } catch (err) {
        loader.classList.add("hidden");
        showToast("Error connecting to AI Assistant", true);
    }
}


// ==========================================
// 7. TOAST NOTIFICATION UTILITY
// ==========================================
function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.backgroundColor = isError ? "var(--color-red)" : "#1e293b";
    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}
