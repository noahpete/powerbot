import Main from "./Main";
import axios from "axios";

// django csrf token verification fix
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";

function App() {
  return (
    <div className="">
      <Main />
    </div>
  );
}

export default App;
