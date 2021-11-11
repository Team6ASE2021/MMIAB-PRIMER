
# API routes
List of endpoints of the API with a brief description

| Endpoint | Description |
| ------ | ------- |
| / | Home endpoint |
| /notification | Returns a JSON with all the notifications for the user |
| /login | Logs the user in |
| /logout | Logs the user out |
| /create_user | Lets the user to create a new account |
| /user/profile | Shows the user profile of the logged user |
| /user/profile/edit | Lets the user edit his own profile |
| /users/\<int:id\> | Shows the user profile of any user |
| /user_list | Shows a list of users |
| /user/delete | Lets the user delete his own account |
| /user/content_filter | Lets the user toggle the content filter option |
| /user/report/\<int:id\> | Lets the user report another user |
| /user/blacklist | Shows the list of blacklisted users by the logged user |
| /user/blacklist/add/\<int:id\> | Lets the user add a new user to the blacklist |
| /user/blacklist/remove/\<int:id\> | Lets the user remove a user from the blacklist |
| /draft | Creates a new message as draft |
| /draft/edit\<int:id\> | Edits a draft |
| /send_message/\<int:id\> | Sends a message |
| /message/\<int:id\>/delete | Lets a recipient delete a read message |
| /draft/\<int:id\>/delete | Lets the creator of a draft delete it |
| /message/\<int:id\>/withdraw | Lets a user withdraw a sent message |
| /message/\<int:id\>/reply | Lets a recipient reply to a received message |
| /forwarding/\<int:id\> | Lets a user forward a sent or received message |
| /recipients | Returns a JSON with all available recipients for the current user |
| /timeline | Shows the timeline moth view for the current month |
| /timeline/day/\<int:year\>/\<int:month\>/\<int:day\>/sent | Shows the timeline day view of sent messages for a specific day |
| /timeline/day/\<int:year\>/\<int:month\>/\<int:day\>/received | Shows the timeline day view of received messages for a specific day |
| /timeline/month/\<int:year\>/\<int:month\> | Shows the timeline moth view for a specific month |
| /read_message/\<int:id\> | Lets an entitled user to read a specific message |
| /message/list/sent | Shows the list of sent messages |
| /message/list/received | Shows the list of received messages |
| /message/list/draft | Shows the list of drafts |
| /lottery/participate | Lets the user participate to the lottery |
| /lottery | Shows the current status of the lottery to the user |



