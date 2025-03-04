import axios from "axios";

const GithubUser = () => {
  // Get return code to get token form GitHub.
  const urlParams = new URLSearchParams(window.location.search);

  function getGithubUser() {

    axios.get(`/api/github/user-info`)
      .then((response) => {
        console.log(response.data.login);
      })
      .catch((error) => {
        console.error("Axios error with request to /login/github");
      });
  }

  return (
    <>
      {/* Send request to backend to check if we're already logged in (ie. have token in this session.) */}
      <button onClick={getGithubUser} className="github-user">Print Github User Info to Console</button>
    </>
  )
}

export default GithubUser;
