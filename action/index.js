const core = require("@actions/core")
const github = require("@actions/github")
const axios = require("axios")

const serverURL = core.getInput("server_url")
const { owner, name } = github.event.repository

axios
    .post(`${serverURL}/deploy`, {
        repo_owner: owner,
        repo_name: name
    })
    .then(res => {
        console.log("done! response:")
        console.log(JSON.stringify(res.data))
    })
    .catch(error => {
        core.setFailed(error.message)
    })
