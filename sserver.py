"""
simple server for hangman gameplay
allows one or 2 player matchup

"""

import select 
import socket 
import sys
import game


if len(sys.argv) > 2:
    host = sys.argv[1],sys.argv[2]
else:
    host = '',50000

 
backlog = 5 
size = 2050
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host))
print ("Hangman game server started on host=" + str(host))

server.listen(backlog)
inputs = [server]
running = 1
versus = game.Match()

while running: 
    inputready,outputready,exceptready = select.select(inputs,[],[]) 

    for s in inputready: 
        if s == server: 
            # handle the server socket 
            client, address = server.accept()  
            inputs.append(client)
        else:
            data = s.recv(size)
            #initialize status messages for both players
            status_message = game.Game_Status()
            status_message_opp = game.Game_Status()
            if (versus.waiting):
                if (data == game.INITIAL_CONNECT_MESSAGE):
                    if (versus.is_two_player == True):
                        #waiting
                        versus.waiting = True
                        versus.players +=1
                        status_message= versus.start_2player(s)
                    else:
                        status_message = versus.prompt_for_multiplayer()
                else:
                    status_message.load_from_json(data)
                    if (status_message.get_status_flag() == game.WAIT_TO_GIVE_WORD):
                        #user is sending word for the opponent
                        status_message, status_message_opp = versus.process_game_response(s, status_message)
                    elif (not versus.process_multi_request(status_message)):
                        status_message = versus.start_1player(s)
                    else:
                        status_message = versus.start_2player(s)

                #send message back to the current client
                s.send(status_message.save_to_json())
                
                #check for opponent connection status and send message to opponent
                #print ("opponent status = " + str(status_message_opp.get_status_flag()))
                #print ("sending opponent =" + status_message_opp.save_to_json())
                if (status_message_opp.get_status_flag() != game.WAIT_FOR_INIT):
                    #print "s= " + str(s) + " socketa=" + str(versus.socketa) + " socketb=" + str(versus.socketb)
                    if (s != versus.socketa) & (isinstance(versus.socketa, socket.socket)):
                        versus.socketa.send(status_message_opp.save_to_json())
                    elif (isinstance(versus.socketb, socket.socket)):
                        versus.socketb.send(status_message_opp.save_to_json())
            else:
                #processing client response
                status_message = game.Game_Status()
                status_message.load_from_json(data)
                status_message, status_message_opp = versus.process_game_response(s, status_message)
                s.send(status_message.save_to_json())
                if (status_message.get_status_flag() > game.IN_PLAY): #game over
                    s.close()
                
    
server.close()
