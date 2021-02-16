//Kayley Johns
//V00915873
//A program that can encode DNA sequence to shorten the letters to the number of letters
//of can take a coded DNA sequence and scan the numbers to output the original letters

#include<stdio.h>
#include<ctype.h>
#include<string.h>
#include<stdlib.h>
#include<dirent.h>

#define MAX_CHAR 80

int encode(char DNA[]);
int decode(char DNA[]);
char short_DNA[MAX_CHAR];
char long_DNA[MAX_CHAR];
int k = 1;
int j = 0;
char *sp;
char *np;
char direct[MAX_CHAR];
int value = 0;
int sum = 1;
int total = 0;

int main(int argc, char *argv[]){
	char DNA[MAX_CHAR];
	int i= 0;
	char c;
	
	if(argc == 1){ //if no directory is given then give error
		printf("Error: No input file specified!\n");
		exit(1);
	}

	if((strcmp(argv[2],"e") != 0) && (strcmp(argv[2],"d")!= 0)){ //if  the first value to the array is not e or d then output an error
		printf("Invalid Usage, expected: RLE{filename} [e | d]\n");
		exit(4);
	} 
	FILE *file_data = fopen(argv[1], "r"); 
	
	if (file_data == NULL) { //if file doesn't exist or does not read then error
		printf("Read error: file not found or cannot be read\n");
		exit(1);
	}

	// Read contents from file and put into the DNA array 
	c = fgetc(file_data); 
    while (c != EOF && sizeof(DNA) != (MAX_CHAR/2)){ 
		DNA[i] = c;
		if(islower(DNA[i])){ //check for an invalid format
			printf("Error: String could not be encoded\n");
			exit(5);
		}
		if(c == ' '){
			while(c == ' ' && c != EOF){
				c = fgetc(file_data);
			}
		
			if(c == EOF){
				break;
			}
			else{
				printf("Error: Invalid format\n");
				exit(3);
			}
		}			

		i++;
		c = fgetc(file_data); 
    } 

	DNA[i] = '\0';

	if(strcmp(argv[2], "e") ==0){ //Based on input either encode or decode
		encode(DNA);
	}else{
		decode(DNA);
	}
	fclose(file_data); 
}
	
	
int encode(char DNA[]){
	
	short_DNA[0] = DNA[0];
	np = &DNA[0];
	np++;

	while(*np != '\0'){
		if((*(np-1) == *np)&& (*(np +1) != '\0')){ //If the value is the same as the last value then add to sum and continue
			sum = sum +1;	                       
		} 
		else if(((*np-1) != *np) && (*np != *(np+1)) && (*(np+1)!= '\0')){ //check if it is a single letter in middle
			if(short_DNA[k-1] != '1'){ //check if value before it was a single letter and put sum in next array spot
				sprintf(&short_DNA[k],"%d", sum);
				k++;
			}
			sum = 1;
			short_DNA[k] = *np;
			k++;
			sprintf(&short_DNA[k], "%d", sum);
			k++;
			sum =0;

		}
		else if((*(np+1) == '\0')&& (*np != *(np-1))){ //check if next value does not equal null and last value does not equal value now
			if(short_DNA[k-1] != '1'){ //checks if letter before was a single letter
				sprintf(&short_DNA[k], "%d", sum);
				k++;
			}
			short_DNA[k] = *np;
			k++;
			short_DNA[k] = '1';	
			break;

		}
		else if(j==0  && *np != *(np-1)){ //checks if there is a single letter in beginning and puts it into the array
			short_DNA[k] = '1';
			k++;
			sum = 0;
		}
		else if(*(np-1) == *np && *(np+1) == '\0'){ //checks if last value is a single letter and puts it into the array
			sum++;
			sprintf(&short_DNA[k], "%d", sum);
			break;
		}
		else{ //otherwise place the sum of the letters in the new array and move to the next letter
			if(short_DNA[k-1] != '1'){ 
				sprintf(&short_DNA[k],"%d", sum);
				k++;
			}
			sum = 1;
			short_DNA[k] = *np;
			k++;
		}
		np++;
		j++;
	}

	if(DNA[1] == '\0'){ //checks if the input is only one letter
		short_DNA[k] = '1';
	}

	sp = &short_DNA[0];
	short_DNA[k+1] = '\0';

	while(*sp != '\0'){
		printf("%c", *sp);
		sp++;
	} 
	printf("\n");
	return 0; 
} 
	
	
	
int decode(char DNA[]){
	while(DNA[value] != '\0'){
		int len;
		if(DNA[value+1] != '\0'){ //checks if next value is null and then turns the char value into an int 
			sscanf(&DNA[value+1], "%d", &len);
		}
	
		while((len) != 0){ //puts the letter in the new array the amount of times the int is 
			long_DNA[total] = DNA[value];
			printf("%c", long_DNA[total]);
			total++;
			len = len -1;
		}


		value = value +2;
	}

	printf("\n"); 
   	return 0; 	
}