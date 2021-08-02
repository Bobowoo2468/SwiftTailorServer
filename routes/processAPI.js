const express = require("express");
const router = express.Router();

router.post("/", function(req,res,next) {
    const spawn = require("child_process").spawn;
    console.log(gender);
    console.log(shoulder);
    console.log(waist);
    const process = spawn('python', ["bodyshape.py", imglink, shoulder, waist, hip, gender]); 
    process.stdout.on('data', function(data){
        console.log(`${data}`); 
        dataToSend = data.toString(); 
        res.send(dataToSend);
    });

});

module.exports=router;