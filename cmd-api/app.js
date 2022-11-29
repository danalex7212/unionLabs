var express = require("express");

const { exec } = require("child_process");

var app = express();
app.listen(3000, () => {
   console.log('listening on port 3000');
});
app.get("/showFolders", (req, res, next) => {
     exec("dir", (error, stdout, stderr) => {
        if (error) {
            console.log(`error: ${error.message}`);
            res.json({"code":501,
                "message":error.message});
        }
        if (stderr) {
            res.json({"code":501,
                "message":"unexpected error occured"});
            return;
        }
        console.log(`stdout: ${stdout}`);
        res.json({code:200,"message":"command executed"});
    });
   });