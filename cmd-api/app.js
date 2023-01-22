var express = require("express");
var fs = require('fs');
//const otpGenerator = require('otp-generator');
const { v4: uuidv4 } = require('uuid');
const { exec, execSync,spawn } = require("child_process");


const sendGridMail = require('@sendgrid/mail');
sendGridMail.setApiKey(process.env.SENDGRID_API_KEY);

var containerData = fs.readFileSync('container.json');
var containerId = JSON.parse(containerData);

var app = express();
app.listen(3000, () => {
   console.log('listening on port 3000');
});

app.get("/startvnc",async (req, res, next) => {
var array = fs.readFileSync('script.exp').toString().split("\n"); //read the template exp file and modify the password with uuid
   let uuid=uuidv4();
   console.log(uuid);
   array[45]=`spawn vncpasswd ${uuid}`;
   array[48]=`send -- "${uuid}\\r"`;
   array[52]=`send -- "${uuid}\\r"`;

   let configStr=array.join('\n');

try {
	console.log("wrting to file");
    fs.writeFileSync('dockervnc.exp', configStr);
    // file written successfully
  } catch (err) {
    console.error(err);
  }

        const firstCommand = spawn('sudo', ['docker', 'run', '-p', `590${req.query.port}:5901`, '-d', 'testvncpass1']); // create a container with vnc server on the required port
        //testvncpass1 is a docker image with vnc server installed and configured

firstCommand.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

firstCommand.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

firstCommand.on('close', (code) => {
  console.log(`child process exited with code ${code}`);

  const secondCommand = spawn('sudo', ['docker', 'ps', '-l', '-q']); // get the containerid of the last container created

  let containerId = '';
  secondCommand.stdout.on('data', (data) => {
    containerId += data;
  });

  secondCommand.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  secondCommand.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    containerId = containerId.trim();

    const thirdCommand = spawn('sudo', ['docker', 'cp', 'dockervnc.exp', `${containerId}:/app`]); // copy the modified exp file to the container

    thirdCommand.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });

    thirdCommand.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });

    thirdCommand.on('close', (code) => {
      console.log(`child process exited with code ${code}`);

      const fourthCommand = spawn('sudo', ['docker', 'exec', containerId, 'expect', '/app/dockervnc.exp']); // run the exp file in the container

      fourthCommand.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
      });

      fourthCommand.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
      });

      fourthCommand.on('close', (code) => {
        console.log(`child process exited with code ${code}`);

        const fifthCommand = spawn('sudo', ['docker', 'exec', containerId, 'vncserver', ':1', '-rfbauth', `${uuid}`]); // start the vnc server with the password

        fifthCommand.stdout.on('data', (data) => {
          console.log(`stdout: ${data}`);
        });

        fifthCommand.stderr.on('data', (data) => {
          console.error(`stderr: ${data}`);
        });

        fifthCommand.on('close', (code) => {
          console.log(`child process exited with code ${code}`);
        });
      });
    });
  });
});
    await (async () => {
                console.log('Sending test email');
                await sendEmail(uuid,`${req.query.email}`); // send the password to the user via email
            })();
    res.json({code:200,"message":"vnc server started.otp sent via email",otp:uuid}); // send the response to the user
          
});
app.get("/endvnc",async (req, res, next) => {
    let containerId = '';
    const firstCommand = spawn('sudo',['docker','ps','-f',`publish=590${req.query.port}`,'-l','-q']); // get the container id of the container running on the required port
	  firstCommand.stdout.on('data',(data) =>{
		  containerId += data;
		  console.log(`stdout: ${data}`)});
	   firstCommand.stderr.on('data', (data) => {
          console.error(`stderr: ${data}`);
        });

        firstCommand.on('close', (code) => {
          console.log(`child process exited with code ${code}`);
		containerId = containerId.trim();
		const secondCommand = spawn('sudo', ['docker', 'stop', containerId]); // stop the container

        secondCommand.stdout.on('data', (data) => {
          console.log(`stdout: ${data}`);
        });

        secondCommand.stderr.on('data', (data) => {
          console.error(`stderr: ${data}`);
        });

        secondCommand.on('close', (code) => {
          console.log(`child process exited with code ${code}`);
		const thirdCommand = spawn('sudo', ['docker', 'rm', containerId]); // remove the container

        thirdCommand.stdout.on('data', (data) => {
          console.log(`stdout: ${data}`);
        });

        thirdCommand.stderr.on('data', (data) => {
          console.error(`stderr: ${data}`);
        });

        thirdCommand.on('close', (code) => {
          console.log(`child process exited with code ${code}`);
        });
        });
        });
	  res.json({code:200,"message":"docker container stopped"});
  });

  
  
  
  
//   app.get("/showFolders", (req, res, next) => {
//     exec("dir", (error, stdout, stderr) => {
//        if (error) {
//            console.log(`error: ${error.message}`);
//            res.json({"code":501,
//                "message":error.message});
//        }
//        if (stderr) {
//            res.json({"code":501,
//                "message":"unexpected error occured"});
//            return;
//        }
//        console.log(`stdout: ${stdout}`);
//        res.json({code:200,"message":"command executed"});
//    });
//   });
//   app.get("/makeFolder", (req, res, next) => {
//    exec("mkdir testfolder", (error, stdout, stderr) => {
//       if (error) {
//           console.log(`error: ${error.message}`);
//           res.json({"code":501,
//               "message":error.message});
//       }
//       if (stderr) {
//           res.json({"code":501,
//               "message":"unexpected error occured"});
//           return;
//       }
//       console.log(`stdout: ${stdout}`);
//       res.json({code:200,"message":"command executed"});
//   });
//  });   

//  app.get("/showalldevices", (req, res, next) => {
//    exec("lsusb", (error, stdout, stderr) => {
//       if (error) {
//           console.log(`error: ${error.message}`);
//           res.json({"code":501,
//               "message":error.message});
//       }
//       if (stderr) {
//           res.json({"code":501,
//               "message":"unexpected error occured"});
//           return;
//       }
//       console.log(`stdout: ${stdout}`);
//       let devices=stdout.split('\n')
//       res.json({code:200,"message":"command executed",
//            result:devices.slice(0,devices.length-1)});
//   });
//  });

//  app.get("/showusrp", (req, res, next) => {
//    exec("lsusb", (error, stdout, stderr) => {
//       if (error) {
//           console.log(`error: ${error.message}`);
//           res.json({"code":501,
//               "message":error.message});
//       }
//       if (stderr) {
//           res.json({"code":501,
//               "message":"unexpected error occured"});
//           return;
//       }
//       console.log(`stdout: ${stdout}`);
//       let devices=stdout.split('\n');
//       const result = devices.filter(word => word.includes("Gaming"));
//       res.json({code:200,"message":"command executed",
//            result:result});
//   });
//  });
//  function getMessage(uuid,email) {
//    const body = `Hey man, this is nice guy. your otp is ${uuid}`;
//    return {
//      to: email,
//      from: 'sylvestertheniceguy@proton.me',
//      subject: 'Hi from nice guy sylvester',
//      text: body,
//      html: `<strong>${body}</strong>`,
//    };
//  }

//  async function sendEmail(uuid,email) {
//    try {
//      await sendGridMail.send(getMessage(uuid,email));
//      console.log('Test email sent successfully');
//    } catch (error) {
//      console.error('Error sending test email');
//      console.error(error);
//      if (error.response) {
//        console.error(error.response.body)
//      }
//    }
//  }


//  app.get("/startvncnull",async (req, res, next) => {
//   var array = fs.readFileSync('script.exp').toString().split("\n");
//   let uuid=uuidv4();
//   console.log(uuid);
//   array[45]=`spawn vncpasswd ${uuid}`;
//   array[48]=`send -- "${uuid}\\r"`;
//   array[52]=`send -- "${uuid}\\r"`;

//   let configStr=array.join('\n');

// try {
//    console.log("wrting to file");
//    fs.writeFileSync('pwdgen.exp', configStr);
//    // file written successfully
//  } catch (err) {
//    console.error(err);
//  }

//    var runScript = exec('./pwdgen.exp',
//        (error, stdout, stderr) => {
//        console.log('excecuting pwdgen.exp script');
//            console.log(stdout);
//            console.log(stderr);
//            if (error !== null) {
//                console.log(`exec error: ${error}`);
//                res.json({"code":501,
//                "message":error.message});
//            }
//        });
//        //vncserver :2 -rfbauth pass2file

//        exec(`vncserver :${req.query.port} -rfbauth ${uuid}`,
//        (error, stdout, stderr) => {
//        console.log('starting vncserver with authentication');
//            console.log(stdout);
//            console.log(stderr);
//            if (error !== null) {
//                console.log(`exec error: ${error}`);
//                res.json({"code":501,
//                "message":error.message});
//            }
//        });
//        // exec(`vncserver  -rfbauth ${uuid}`, (error, stdout, stderr) => {
//        //     if (error) {
//        //         console.log(`error: ${error.message}`);
//        //         res.json({"code":501,
//        //             "message":error.message});
//        //     }
//        //     if (stderr) {
//        //         //console.log(stderr);
//        //         res.json({"code":501,
//        //             "message":"unexpected error has occured"});
//        //         return;
//        //     }
//        //     console.log(`stdout: ${stdout}`);
//        //     res.json({code:200,"message":"vnc server started",otp:uuid});
//        // });
       
//      await (async () => {
//            console.log('Sending test email');
//            await sendEmail(uuid,`${req.query.email}`);
//          })();
       
//          res.json({code:200,"message":"vnc server started.otp sent via email",otp:uuid});

//  });  
// app.get("/endvncnull",async (req, res, next) => {
// exec(`vncserver -kill :${req.query.port}`,
//        (error, stdout, stderr) => {
//            console.log(stdout);
//            console.log(stderr);
//            if (error !== null) {
//                console.log(`exec error: ${error}`);
//                res.json({"code":501,
//                "message":error.message});
//            }
//        });
// res.json({code:200,"message":"vnc server stopped"});

// });
