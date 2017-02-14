#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "jsmn.h"

/*
 * A small example of jsmn parsing when JSON structure is known and number of
 * tokens is predictable.
 */

static const char *JSON_STRING =
	"{\"user\": \"johndoe\", \"admin\": false, \"uid\": 1000,\n  "
	"\"groups\": [\"users\", \"wheel\", \"audio\", \"video\"]}";
 
static const char *cmd1 = "{\"category\":\"BN_LED\",\"id\":\"34\", \"value\":\"3\"}";
static const char *cmd2 = "{\"category\":\"BN_LED\",\"id\":\"ALL\", \"value\":\"3\"}";
static const char *cmd = "{\"category\":\"BN_LED\",\"id\":[\"34\",\"45\"], \"value\":\"3\"}";  

static int jsoneq(const char *json, jsmntok_t *tok, const char *s) {
	if (tok->type == JSMN_STRING && (int) strlen(s) == tok->end - tok->start &&
			strncmp(json + tok->start, s, tok->end - tok->start) == 0) {
		return 0;
	}
	return -1;
}

int main() {
	int i;
	int r;
  char value[32];
  char id[32];
  int id_arr[16];
  char category[32];
  char temp[32];
	jsmn_parser p;
  long int temp_long;
  long t_array[16];
  int arr_size = 0;
  char *temp_ptr;
	jsmntok_t t[128]; /* We expect no more than 128 tokens */

	jsmn_init(&p);
	r = jsmn_parse(&p, cmd, strlen(cmd), t, sizeof(t)/sizeof(t[0]));
	if (r < 0) {
		printf("Failed to parse JSON: %d\n", r);
		return 1;
	}

	/* Assume the top-level element is an object */
	if (r < 1 || t[0].type != JSMN_OBJECT) {
		printf("Object expected\n");
		return 1;
	}

	/* Loop over all keys of the root object */
	for (i = 1; i < r; i++) {
		if (jsoneq(cmd, &t[i], "category") == 0) {
			/* We may use strndup() to fetch string value */
			printf("- category: %.*s\n", t[i+1].end-t[i+1].start,
					cmd + t[i+1].start);
			i++;

		} else if (jsoneq(cmd, &t[i], "value") == 0) {
			/* We may want to do strtol() here to get numeric value */
      sprintf(value, "%.*s\n", t[i+1].end-t[i+1].start,cmd+t[i+1].start);
      printf("%s\n", value);
			printf("- value: %.*s\n", t[i+1].end-t[i+1].start,
					cmd + t[i+1].start);
			i++;
		} else if (jsoneq(cmd, &t[i], "id") == 0) {
			int j;
			printf("- id:\n");
			if (t[i+1].type != JSMN_ARRAY) {
  		printf("- single led: %.*s\n", t[i+1].end-t[i+1].start,
				  	cmd + t[i+1].start);
			  i++;		
		}else{
        
  			for (j = 0; j < t[i+1].size; j++) {
          
  				jsmntok_t *g = &t[i+j+2];
          sprintf(temp, "%.*s\n", g->end - g->start, cmd + g->start);
          temp_long = strtol(temp, &temp_ptr, 10);
          t_array[j] = temp_long;
          printf("%d\n", temp_long);
          arr_size++;
  			}
  			i += t[i+1].size + 1;
        }        
		} else {
			printf("Unexpected key: %.*s\n", t[i].end-t[i].start,
					cmd + t[i].start);
		}
	}
   size_t size = sizeof(t_array)/sizeof(long);
  for(i=0;i<arr_size;i++){
    printf("a: %d\n", t_array[i]);
  }
	return EXIT_SUCCESS;
}