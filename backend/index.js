const express = require("express");
const cors = require("cors");

const app = express();

// middleware
app.use(cors());
app.use(express.json());

// ===== ROUTES =====

// test route
app.get("/", (req, res) => {
  res.send("Backend is running");
});

// hello API
app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello from backend" });
});

// students API
app.get("/api/students", (req, res) => {
  const students = [
    { id: 1, name: "Amit", course: "Basic Computer" },
    { id: 2, name: "Riya", course: "Tally" },
    { id: 3, name: "Suman", course: "Python" }
  ];
  res.json(students);
});

// auth routes 👈 THIS WAS MISSING
const authRoutes = require("./routes/auth");
app.use("/api/auth", authRoutes);

// ===== SERVER =====
const PORT = 5000;
app.listen(PORT, () => {
  console.log("Server running on http://localhost:" + PORT);
});
