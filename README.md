# TempuBot
This is a discord bot developed by Archmage Tempia of the guild Hive Mind on Zandalar Tribe. The bots main purpose is to help with the administration of the guild.

## Commands

### Echo
This command echoes whatever you write back and deletes your message. If only the command is called, it replies 'echo'. The primary purpose of this command is debugging and lulz.  
Example use:  
`!echo` the bot replies 'echo'.  
`!echo Matitka Sucks!` the bot replies 'Matitka Sucks!'. Good bot.  

### Attendance
This command is used to get a bar graph of the raiders' attendances.  
Optionally includes arguments for how far to go back.  
Example use:  
`!attendance` shows all registered attendance as a horizontal bar graph.  
`!attendance 3` or `!attendance 3 months` takes attendance for the last 3 months.  
`!attendance 3 days` takes attendance for the last three days.  

#### Inspect
If the command is followed by the keyword 'inspect', the bot will inspect the name(s) in the message. The bot can display the information in three ways: ordinary (no option), verbose (`-v`) and brief (`-b`). This option can be inserted anywhere after the 'inspect' keyword. As with the parent command, it optionally includes an argument for how far to go back.  
Example use:  
`!attendance inspect matitka` shows the attendance of the raider 'matitka'.  
`!attendance inspect matitka saasen` shows the attendances of the raiders 'matitka' and 'saasen'.  
`!attendance inspect -v matitka saasen 45 days` shows the attendances (including dates, thanks to `-v`) of the raiders 'matitka' and 'saasen' for the last 45 days.

#### Class
If the command is followed by the keyword 'class', the bot will inspect the class(es) in the message. As with the parent command, it optionally includes an argument for how far to go back.  
Example use:  
`!attendance class warrior` shows the attendance of the guilds warriors.  
`!attendance class mage warlock priest` shows the attendance of the guilds mages, warlocks and priests.  

### Listraids
This command lists the raids in the schedule. The schedule is used to limit the amount of spam we cause to the warcraftlogs server. The bot will only check for new boss kills within the windows specified by the schedule.  
Example use:  
`!listraids`

### Addraid
This command will add a raid to the schedule. Don't use this command unless you need to and you're supervised by an adult.  
Example use:  
`!addraid sunday 19.30 sunday 23.00` adds the sunday raid to the schedule.

### Removeraid
This command will remove a raid from the schedule. Note you will need the index from `!listraids` to specify which raid to remove.  
Example use:  
`!removeraid 1` removes the second(!) raid from the schedule - the one with the index 1 in `!listraids`.

### Forget
A big part of being able to make the boss fight summaries is to have a record of which bosses we kill each week. This command will remove the boss from that record. This causes the bot to make a new summary of the kill. It is mostly used for debugging purposes and can be used to reprint a summary if needed. The bot will guess which boss you mean by the input. It is not necessary to write out the entirity of the boss' name.  
Example use:  
`!forget Ragnaros` removes Ragnaros from the boss kill record.  
`!forget majo` removes Majordomo Executus from the boss kill record.  
