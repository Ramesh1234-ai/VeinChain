
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
  import { getFirestore, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

  // IMPORTANT: Move Firebase config to Backend/.env or Backend/firebase_config.json
  // DO NOT store credentials in frontend code
  const firebaseConfig = window.FIREBASE_CONFIG || {
    apiKey: "REPLACE_WITH_YOUR_API_KEY",
    authDomain: "REPLACE_WITH_YOUR_AUTH_DOMAIN",
    projectId: "REPLACE_WITH_YOUR_PROJECT_ID",
    storageBucket: "REPLACE_WITH_YOUR_STORAGE_BUCKET",
    messagingSenderId: "REPLACE_WITH_YOUR_SENDER_ID",
    appId: "REPLACE_WITH_YOUR_APP_ID",
    measurementId: "REPLACE_WITH_YOUR_MEASUREMENT_ID"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const db = getFirestore(app);

  // Attach login handler (only once!)
  document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    if (!email || !password) {
      alert("Email and password are required");
      return;
    }

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok) {
        // Save token + user in localStorage
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("userData", JSON.stringify(data.user));

        // Log login event into Firestore (if configured)
        try {
          await addDoc(collection(db, "loginEvents"), {
            email: email,
            role: data.user.role || "unknown",
            timestamp: serverTimestamp()
          });
        } catch (firestoreError) {
          console.warn("Could not log to Firestore:", firestoreError);
        }

        // Redirect based on role
        const role = data.user.role;
        if (role === "admin") {
          window.location.href = "adminPanel.html";
        } else if (role === "donor") {
          window.location.href = "dashboard.html";
        } else if (role === "recipient") {
          window.location.href = "Recipent.html";
        } else {
          window.location.href = "index.html";
        }

      } else {
        alert(data.error || "Login failed.");
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("Network or server error.");
    }
  });
