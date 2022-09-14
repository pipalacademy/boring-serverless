const core = require("@actions/core")
const github = require("@actions/github")
const axios = require("axios")

const serverURL = core.getInput("server_url")
const appName = core.getInput("app_name")

axios
    .post(`${serverURL}/apps/${appName}/deploy`)
    .then(res => {
        console.log("done! response:")
        console.log(JSON.stringify(res.data))
    })
    .catch(error => {
        core.setFailed(error.message)
    })
