Sensei Doro
-----------
[![Discord Bots](https://top.gg/api/widget/status/928304609636794388.svg)](https://top.gg/bot/928304609636794388)
[![Discord Bots](https://top.gg/api/widget/servers/928304609636794388.svg?noavatar=true)](https://top.gg/bot/928304609636794388)
[![Discord Bots](https://top.gg/api/widget/upvotes/928304609636794388.svg?noavatar=true)](https://top.gg/bot/928304609636794388)

A Discord Bot that automatically manages your study group using the Pomodoro Technique.    
If you enjoy my work, consider supporting me on [Ko-fi](https://ko-fi.com/shroominic) :)

### [**Invite Sensei Doro**](https://discord.com/api/oauth2/authorize?client_id=928304609636794388&permissions=21048400&scope=bot%20applications.commands)  to your discord server and get started with `/help`.
###### Please keep in mind that the bot will not work properly if you do not accept all required permissions.

The Idea
--------
The **Pomodoro Technique** is a time management method that has been used to boost productivity for students and workers since 1980.
A *Pomodoro* was typically `25 minutes of work` with `5 minutes break`, tracked using a *Pomodoro timer* (a tomato kitchen timer).
After completing four Pomodoros, you would take an extended break (15-30 minutes) and begin the process again.


**Group study** has been around for as long as education itself. By working in a group, you boost the motivation for yourself and other group members.   
Learning becomes much easier and more enjoyable through discussion of the content, and the group members can keep each other accountable.
Working alone and being in an online study room will help you better learn because it gives you some kind of social pressure that you should learn instead of procrastinating.  
In addition, it is simply comforting to know you are not alone and other people are working hard alongside you!


**Sensei Doro** combines these techniques and brings them to the *Discord* voice and chat platform in the form of an easy-to-use bot.  
Your mates from all around the world can use Sensei Doro to work together as a group, sharing a flexible Pomodoro-style group timer that notifies them when to take a break and when to start work again.
Whether you work at night or in the day, you never need to be alone!


Features
-----------
* Sensei Doro shows a timer with your work/break time.
* When you start a new study session, it starts automatically for all your peers waiting inside the lobby channel.
* During work time, everyone is muted, during the break, you can talk with your study mates.
* You can control the session with different `/session` commands

Demo
----
![Giphy Gif](https://media.giphy.com/media/rFieX21uO4a97o8GTB/giphy.gif)

Commands
--------
You can interact with the bot using discord `/` slash commands.  

###### Notation: `<required argument>` , `[optional arg]{default value}` , `<'subcommands'|'to'|'choose'|'from'>`   

### Setup
* Show help information: `/help`   
- Create a new pomodoro environment: `/create [name]{"Pomorodo"} [work_time]{25} [break_time]{5} [repetitions]{4}`   


### Session
* Start a session: `click on *START SESSION*`
- Edit the session: `/session edit <'name'|'work_time'|'break_time'|'repetitions'> <value>`
* Force a break: `/session break`
- Delete a session environment: `/session delete`
* Reset a session to the initial state: `/session reset`

### Admin
- General configuration: `/config <'mute_admins'| > <true/false>` (more coming soon)
* Set your own roles to control command permissions: `/role <'admin'|'moderator'> <@your_role>`
- Delete/Reset all data Sensei Doro knows about this guild: `/data <'delete'|'reset'>`
