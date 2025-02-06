<h1>This repo contains instructions for Creating HTTP requests and working with AWS Lambda functions.</h1>
<h2>Packaging up Requests</h2>
<p>AWS Lambda only has the basic python builtin Libraries as default. Requests is an abstract library that is built on the underlying urllib packages using APIs. This means that to use the requests library and functions, we need to upload the whole library as a package.</p>
<p>Here is a detailed step by step for uploading the Requests library as a zip file to Lambda: https://medium.com/@cziegler_99189/using-the-requests-library-in-aws-lambda-with-screenshots-fa36c4630d82</p>
<p>In short:</p>
<li>Create a new file on your PC</li>
<li>Open a shell in the new directory and import the request module into it with the command: <i>pip3 install requests -t . --no-user</i> </li>
<li>Compress the file and upload it to your Lambda function</li>
<li>Manually move the Library and it s dependancies out of the uploaded file so they are in the top lvel directory of the function</li>




