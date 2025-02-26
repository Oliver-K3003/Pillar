import axios from "axios";

const GithubRateLimit = () => {
  // Get return code to get token form GitHub.
  const urlParams = new URLSearchParams(window.location.search);

  function getGithubRateLimit() {

    axios.get(`/api/github/rate-limit`)
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.error("Axios error with request to /github/rate-limit");
      });
  }

  return (
    <>
      {/* Send request to backend to check if we're already logged in (ie. have token in this session.) */}
      <button onClick={getGithubRateLimit} className="github-rate-limit">Print Github Rate Limit</button>
    </>
  )
}

export default GithubRateLimit;
