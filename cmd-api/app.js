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
   app.get("/makeFolder", (req, res, next) => {
    exec("mkdir testfolder", (error, stdout, stderr) => {
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

  app.get("/showalldevices", (req, res, next) => {
    exec("lsusb", (error, stdout, stderr) => {
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
       let devices=stdout.split('\n')
       res.json({code:200,"message":"command executed",
            result:devices.slice(0,devices.length-1)});
   });
  });

  app.get("/showusrp", (req, res, next) => {
    exec("lsusb", (error, stdout, stderr) => {
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
       let devices=stdout.split('\n');
       const result = devices.filter(word => word.includes("Gaming"));
       res.json({code:200,"message":"command executed",
            result:result});
   });
  });