import axios from "axios";
import { useEffect, useState } from 'react';

const GithubLogin = () => {
  // Get return code to get token form GitHub.
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");
  const [data, setData] = useState(null);
  const [isDisabled, setIsDisabled] = useState(false);

  useEffect(() => {
    console.log("useEffect() for 'code' variable.");
    const token = sessionStorage.getItem("githubToken");


    if (token) {
      console.log("Has token, getting authorization.");
      const token = sessionStorage.getItem("githubToken");
      axios.get("https://api.github.com/user", {
        headers: { Authorization: token },
      }).then((response) => {
        console.log(response.data);
      }).catch((error) => {
        console.error(error);
      });
    } else if (code) {
      console.log("Code: " + code);
      axios.get(`http://localhost:5000/exchange-code-for-token`, {
        params: {
          code: code,
          state: "YOUR_RANDOMLY_GENERATED_STATE",
        },
      }).then((response) => {
        const data = response.data;
        setData(data);
        sessionStorage.setItem("githubToken", `${data.token_type} ${data.access_token}`);
      }).catch((error) => {
        console.error("Axios Error:", error);
      })
    }
  }, [code]);

  function githubLoginRedirect() {
    // When user clicks button, redirect to GitHub to get the neccessary access.
    console.log("githubLoginRedirect()");
    const client_id = "Ov23lipp1FKM5Lltmvw0"; // Move to env file after lol
    const redirect_uri = "http://localhost:3000/";
    const scope = "read:user repo";
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${client_id}&redirect_uri=${redirect_uri}&scope=${scope}`;
    window.location.href = authUrl;
  }

  return (
    <>
      <button onClick={githubLoginRedirect} className="github-login">Login Using GitHub</button>
    </>
  )
}

export default GithubLogin;
