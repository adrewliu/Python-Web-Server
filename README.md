# Python-Web-Server
Web server that accepts files and saves the HTTP Response message output in a CSV and text file.
1. Start the Web Server by using this command:
        - python3 [python file] -p [port #] -d [directory]
2. Test the Web Server by using any of these commands on the command line:
        - wget http://[server IP]:[port #]/[filename]
        - curl http://[server IP]:[port #]/[filename]
3. Test the Web Server from the browser by entering:
        - http://[server IP]:[port #]/[filename]
4. Error Handling:
        - Entering a port number other than 80 will result in an error
          message to be outputted.
        - Attempting to read a non-existent file will result in a 404 File
          Not Found error. The HTTP response will be added into the text
          file with the content-length set to 0 and the last-modified date
          set to None. The HTTP response will be included in the CSV file
          with the number of bytes sent set to 0.
        - Attempting to use a HTTP request method other than the HTTP GET
          method will result in a 501 Not Implemented error. The 4 tuple
          of the file will be added into the CSV file if it exists and the
          HTTP response will be included in the text file.
