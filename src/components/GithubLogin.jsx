import React, { useEffect, useState } from 'react';

const GithubLogin = () => {
  // Get return code to get token form GitHub.
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");
  const [data, setData] = useState(null);
  const [isDisabled, setIsDisabled] = useState(false);

  useEffect(() => {
    console.log("useEffect() for 'code' variable.");
    const token = localStorage.getItem("githubToken");

    if (token) {
      console.log("Has token, getting authorization.");
      const token = localStorage.getItem("githubToken");
      fetch("https://api.github.com/user", {
				headers: { Authorization: token },
			})
				.then((res) => res.json()) // Parse the response as JSON
				.then((data) => {
          console.log(data);
				});
    } else if (code) {
      console.log("Code: " + code);
      fetch(`http://localhost:5000/exchange-code-for-token?code=${code}&state=YOUR_RANDOMLY_GENERATED_STATE`)
        .then((res) => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json(); // Parse the JSON response
        })
        .then((data) => {
          setData(data);
          localStorage.setItem("githubToken", `${data.token_type} ${data.access_token}`);
        })
        .catch((error) => {
          console.error("Fetch Error:", error); // Log errors to the console
        });
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
      <button onClick={githubLoginRedirect}>Login Using GitHub</button>
    </>
  )
}

export default GithubLogin;