
  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-app.js";
  import { getAuth,GoogleAuthProvider,signInWithPopup } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-auth.js";

  import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-analytics.js";
  
  // IMPORTANT: Move Firebase config to Backend/.env or Backend/firebase_config.json
  // DO NOT store credentials in frontend code
  // Load from backend API or environment variables
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
  const auth = getAuth(app);
  auth.languageCode = 'en';
  const googlelogin = document.getElementById("google-login");
const provider = new GoogleAuthProvider();
provider.setCustomParameters({ prompt: "select_account" });

googlelogin.addEventListener("click", async () => {
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        const idToken = await user.getIdToken();

        const res = await fetch("/api/auth/firebase-login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idToken: idToken })
        });

        const data = await res.json();
        console.log("Backend verified:", data);

        if (data.success) {
            window.location.href = "dashboard.html";
        } else {
            alert("Login failed: " + (data.message || data.error));
        }
    } catch (error) {
        console.error("Error during login:", error);
        alert("Login error. Check console for details.");
    }
});

  const analytics = getAnalytics(app);
