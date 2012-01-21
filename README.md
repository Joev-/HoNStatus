# HoNStatus - A HoN Server Monitor

This is a back-end program that I wrote to complement a [web front-end](http://honstatus.winsauce.org) which displays the current 
status of the HoN servers. It was originally intended to be a website that would exist that players could consult when they are 
having connectivity problems, but it lost traction and was never publicly completed. I have developped it in my spare time as a 
hobby and method of learning, along with developing [HoNCore](http://github.com/Joev-/HoNCore). 

As I am no longer playing HoN I wish to release the code for this to the public so that they can learn from it and if they wish to, are
fully free to use it as they please.

## Usage

The program runs in a terminal and uses a Heroes of Newerth account to log in to the servers in order to test their connectivity.
Currently the configuration is stored in a mysql database, however it can be moved to a config file, this was just how I had it set up.  

Run `python main.py` in a terminal to start the program. It will then attempt to connect and then report any errors it encounters.  
After 5 minutes it will disconnect and run the log in process again. This is repeated indefinately.  
The program can be ended using c-C (Control-C). I recommend using a process monitor such as [Supervisor](http://supervisord.org/) to run the monitor.

The program will put the status of the Login and Chat servers into a database, and it will monitor the number of players online as well.
I planned to migrate to Postgresql for the database, but that has yet to happen, so for now, all I have is a MySQL schema which you can import to create
the database.


## Database Setup

Create a database named `honstatus` and run the following command to import the database schema.  

`mysql -u user -p honstatus < honstatus_schema.sql`  

When that's done you will need to fill out the settings table with some default values that you can modify.  

`mysql -u user -p honstatus < settings_default.sql`  

That should leave you ready to run the program.

## Web Front-End

The front end for the website is available at [HoNStatus-Frontend](http://github.com/Joev-/HoNStatus-Frontend). Please note that the code is very scrappy and has been pending a re-write for many a months.

## License

_This is free and unencumbered software released into the public domain._

_Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means._

_In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law._

_THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE._

_For more information, please refer to <http://unlicense.org/>_

