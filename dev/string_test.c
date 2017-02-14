#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "jsmn.h"

struct Command{
  char category[7];
  char id[4];
  char value[4];
}command;

void parse_command(char *cmd, struct Command *command){
	int i;
	char cat[7];
  char id[4];
  char value[4];  
  
	for(i=13;i<19;i++){
		cat[i-13] = cmd[i];
    cat[6] = '\0';
	}
  for(i=27;i<30;i++){
    id[i-27] = cmd[i];
    id[3] = '\0';
  }
  for(i=42;i<45;i++){
    value[i-42] = cmd[i];
    value[3] = '\0';
  }
  printf("Cat: %s\n", cat);
  printf("ID: %s\n", id);
  printf("Value: %s\n", value);
  strcpy(command->category, cat);
  strcpy(command->id, id);
  strcpy(command->value, value);
   
}

int main(){
  char cmd[64] = "{\"category\":\"BN_LED\",\"id\":\"034\", \"value\":\"003\"}";
  
     
  //struct Command command;
  //parse_command(cmd, &command);
  char * pch;
  //printf ("Splitting string \"%s\" into tokens:\n",str);
  pch = strtok (cmd," ,.-");
  while (pch != NULL)
  {
    printf ("%s\n",pch);
    pch = strtok (NULL, "\"}");
  }
  return 0;
}
  
  
  //printf("%s\n", command.category);
