# TempuBot
This is a discord bot developed by Archmage Tempia of the guild Hive Mind on Zandalar Tribe. The bots main purpose is to help with the administration of the guild.

## Commands

### Echo
(**admin**, **officer**)
This command echoes whatever you write and deletes your message. The primary purpose of this command is debugging and lulz.  
Example use:  
`!echo` pls dont do this.  
`!echo Matitka Sucks!` the bot replies 'Matitka Sucks!. Good bot.  

### Ann
(**admin**, **officer**)
This commands echoes your message into the announcement channel as an announcement. It appends the *annend* message to the end as a sign off.  
Example use:  
`!ann @Tempia is amazing.` would make a very redundant announcement.

### Annend
(**admin**)
This command sets the announcement sign off.  
Example use:  
`!annend -Hive Mind Officer Team` sets an appropriate announcement sign off.

### Announcementchannel
(**admin**)
This command sets the current channel as the announcement channel, making the bot post in here when `!ann` is used.  
Only use:  
`!announcementchannel` sets the announcement channel.

### Welcome
(**admin**, **officer**)
This command just echoes the current welcome message. This allows us to see the welcome message without rejoining the server.  
Example use:  
`!welcome` the bot replies with the welcome message.

### Setwelcome
(**admin**)
This command is used to set the welcome message.  
Example use:  
`!setwelcome x3 nuzzles! pounces on you uwu you so warm` sets a very uwu welcome message.  

### Enable
(**admin**)
This command enables the use of another command if it has been disabled. Currently only the clear command can be disabled.  
Example use:  
`!enable clear` enables the use of the clear command.

### Disable
(**admin**)
This command disables the use of another command. Can only be used on clear currently.  
Example use:  
`!disable clear` disables the use of the clear command.

### Clear
(**admin**)
This command clears messages from the channel it is sent in. The command takes one or both of two arguments: which members messages to clear and how many messages to clear.  
Example use:  
`!clear 15` clears the last 15 messages in the channel.  
`!clear @Matitka` clears the messages sent by Matitka within the last 100 messages in the channel.  
`!clear @Matitka 15` clears the last 15 messages sent by Matitka.

### Clearuntil
This command clears messages until it reaches the message that matches the argument. Matching, in this case, means that the message will match the argument from the beginning of the message. If the target message to clear until is 'Matitka should just get better at the game tbh', 'Matitka should just' would work and 'should just get better' would **not** work. The matching is case sensitive so 'matitka should just' wouldn't work either. In addition, the command is also sensitive to formatting like **bold** and *italic* text. The primary use of this is to copy-paste the taget message.  
Example use:  
`!clear Matitka should just` clears all messages up to and including the latest message that starts with 'Matitka should just'.

### Attendance
(**admin**, **officer**)
This command is used to see the attendance of specific raiders or all raiders from specific classes. Optionally includes arguments for how far to go back.  
Example use:  
`!attendance matitka` shows the attendance of the raider 'matitka'.  
`!attendance matitka saasen 45 days` shows the attendances of the raiders 'matitka' and 'saasen' for the last 45 days.  
`!attendance warrior` shows the attendance of the guilds warriors.  
`!attendance mage warlock priest` shows the attendance of the guilds mages, warlocks and priests.  
`!attendance mage izomi drainz warrior` shows the attendance of the guilds mages and warriors along with 'izomi' and 'drainz'.

### Attendanceplot
(**admin**, **officer**)
This command is used to get a bar graph of the raiders' attendances. Optionally includes arguments for how far to go back.  
Example use:  
`!attendanceplot` shows all registered attendance as a horizontal bar graph.  
`!attendanceplot 3` or `!attendanceplot 3 months` takes attendance for the last 3 months.  
`!attendanceplot 3 days` takes attendance for the last three days. 

### Signoff
(**everyone**)[DM the bot] Signs off to the bot, registering the signoff and posting it to the officer signoff channel. The formatting of the message is important: `!signoff NAME DATE REASON` or `!signoff NAME DATE-DATE REASON`. Note the date is MM.DD or MM/DD. The reason can be left out.  
Example use:  
`!signoff matitka 26.01 Playing retail :kekW:` results in the message 'Matitka signed off for Sunday the 26th of January. Reason: "Playing retail :kekW:"'  
`!signoff Tempia 15.01-01.02 On holiday after writing this dumb bot` results in the message 'Tempia signed off from the 15th of January to the 1st of February. Reason: "On holiday after writing this dumb bot"'  

### Signoffs
(**admin**, **officer**)
This command is used to see all sign offs for a raid easily. It takes the date as an argument.
Example use:  
`!signoffs 12.01` makes the bot post the sign offs and what the remaining raid setup is for the 12th of January.

### Setsignoffschannel
This command makes the bot post the signoff messages to the current channel.  
Example use:  
`!setsignoffschannel` sets the signoffs channel to the current channel.

### Lr
(**admin**, **officer**)
This command lists the raids in the schedule. The schedule is used to limit the amount of spam we cause to the warcraftlogs server. The bot will only check for new boss kills within the windows specified by the schedule.  
Example use:  
`!listraids`

### Ar
(**admin**)
This command will add a raid to the schedule. Don't use this command unless you need to and you're supervised by an adult.  
Example use:  
`!addraid sunday 19.30 sunday 23.00` adds the sunday raid to the schedule.

### Rr
(**admin**)
This command will remove a raid from the schedule. Note you will need the index from `!listraids` to specify which raid to remove.  
Example use:  
`!removeraid 1` removes the second(!) raid from the schedule - the one with the index 1 in `!listraids`.

### Forget
(**admin**, **officer**)
A big part of being able to make the boss fight summaries is to have a record of which bosses we kill each week. This command will remove the boss from that record. This causes the bot to make a new summary of the kill. It is mostly used for debugging purposes and can be used to reprint a summary if needed. The bot will guess which boss you mean by the input. It is not necessary to write out the entirity of the boss' name.  
Example use:  
`!forget Ragnaros` removes Ragnaros from the boss kill record.  
`!forget majo` removes Majordomo Executus from the boss kill record.  

## Todo
1. Message that makes reactions cause role changes.
2. Performance inspect.
- Loot sheet interaction
