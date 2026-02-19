document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab-btn");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const loginForm = document.getElementById("loginForm");
  const errorMsg = document.getElementById("errorMsg");

  let selectedRole = "student"; // default

  // Switch role tabs
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      selectedRole = tab.getAttribute("data-role");
      errorMsg.innerText = "";
    });
  });

  // Handle login
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (!email.endsWith("@kusoed.edu.np")) {
      errorMsg.innerText = "Use your college email (name@kusoed.edu.np)";
      return;
    }

    if (selectedRole === "student") {
      window.location.href = "student.html";
    } else if (selectedRole === "teacher") {
      window.location.href = "teacher.html";
    } else if (selectedRole === "admin") {
      window.location.href = "admin.html";
    }
  });
});
//charts
// document.addEventListener("DOMContentLoaded", () => {
//   const lineCtx = document.getElementById("lineChart").getContext("2d");
//   new Chart(lineCtx, {
//     type: "line",
//     data: {
//       labels: ["Jan", "Feb", "Mar", "Apr", "May"],
//       datasets: [{
//         label: "Attendance %",
//         data: [85, 88, 90, 87, 89],
//         borderColor: "#0984e3",
//         backgroundColor: "rgba(0, 184, 148, 0.2)",
//         fill: true,
//         tension: 0.3
//       }]
//     },
//     options: {
//       responsive: true,
//       scales: {
//         y: { beginAtZero: true, max: 100 }
//       }
//     }
//   });

//   const barCtx = document.getElementById("barChart").getContext("2d");
//   new Chart(barCtx, {
//     type: "bar",
//     data: {
//       labels: ["ITEX 101", "ITEX 213", "ITEX 300", "VPED 301"],
//       datasets: [{
//         label: "Attendance %",
//         data: [90, 84, 95, 90],
//         backgroundColor: ["#00b894", "#fdcb6e", "#0984e3", "#2d3436"]
//       }]
//     },
//     options: {
//       responsive: true,
//       scales: {
//         y: { beginAtZero: true, max: 100 }
//       }
//     }
//   });
// });
