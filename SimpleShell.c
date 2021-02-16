//A very simple unix shell that takes commands and creates child processes to 
//run those commands. Does outfile and piping

#include <stdio.h>                                                                 
#include <stdlib.h>
#include <string.h>                                                                
#include <unistd.h>
#include <wait.h>                                                                  
#include <sys/types.h>
#include <sys/stat.h>                                                              
#include <fcntl.h>

#define MAX_INPUT_LINE 80
#define MAX_INPUT 9

int main(int argc, char *argv[]) {
    char input[MAX_INPUT_LINE];
    int  line_len;
    FILE *fp;
    int lines;
    char *outfile;
    char *token[MAX_INPUT];
    char *find_path[MAX_INPUT];
    char *find_path2[MAX_INPUT];
    char *find_path3[MAX_INPUT];
    char *t;
    char path[200][200];
    char *arg_val[MAX_INPUT];
    char *arg_val2[MAX_INPUT];
    char *arg_val3[MAX_INPUT];
    int i,s,m,l,w;
    int fd1;
    int count_pipe;
    char temp[200][200] ;
    char temp2[200][200];
    char temp3[200][200];
    char letter[200];
    char *result[200][200];
    struct stat buffer;
    char *cmd_path;
    char *cmd_path2;
    char *cmd_path3;
    int pid,status;
    char *envp[] = { 0 };
    int valid_cmd,out,pipe_true;
    int pid_head, pid_middle, pid_tail;                                                
    int fd[2],fd2[2];
    
    //open the rc file and read each of the directories in and store into a array      
    fp = fopen(".sh360rc" ,"rb");
    lines = 0;                                                                     
    while (fgets(letter,200,fp)!= NULL){
        strcat(path[lines],letter);
        lines++;
    }

    //Start a loop to keep accepting commands until exit is typed
    for(;;) {
        fprintf(stdout, "> ");
        fflush(stdout);
        memset(token,0, sizeof token);
        cmd_path = NULL;
        out = 0;
        pipe_true = 0;                                                             
        //tokens = token(&num_tokens);


        //This was taking from appendix a to read in the command
        //and store it in an array
        fgets(input, MAX_INPUT_LINE, stdin);
        if (input[strlen(input) - 1] == '\n') {
            input[strlen(input) - 1] = '\0';
        }
        //This copies all of the directories to a temp array
        //It also adds a / to end of each of the paths
        memset(temp,0,sizeof temp);
        int num_tokens = 0;
        int m = 0;
        for(int l=0;l<lines;l++){
                m = 0;
                strcat(temp[l],path[l]);
                while(temp[l][m] != '\n'){
                        m++;                                                                       
                }
                if (temp[l][m-1] != '/'){                                                                  
                    temp[l][m] = '/';
                    temp[l][m+1] = '\0';                                                       
                }else{
                     temp[l][m] = '\0';                                                         
                }
        }


        //This was taken from appendix e to tokeinize the command so that
        //each part is stored in the token array
        t = strtok(input, " ");
        while (t != NULL && num_tokens < MAX_INPUT) {
            token[num_tokens] = t;
            num_tokens++;
            t = strtok(NULL, " ");
        }

        //count the amount of -> in the command to see if this is three                    
        //pipes and increament the count_pipe value each time
        count_pipe = 0;
        for(int p=0;p<num_tokens;p++){
            if(strcmp(token[p],"->") == 0){
                count_pipe++;

            }
        }
        //Check to see if the input is exit and if so then exit the program
        if(strcmp(input, "exit") == 0){
                fclose(fp);
                exit(0);
        }

        valid_cmd = 0;
        int count = 1;
        //See if the first command is OR and make the path set to the second
        //command in the array
        if(strcmp(token[0],"OR") == 0){
            find_path[0] = token[1];                                                           
            //while not -> keep placing the commands into the arg_val array
            while(strcmp(token[count],"->") != 0){                                                  
            arg_val[count-1] = token[count];
                 count++;                                                                      
                 }
            //if the format of the command entered is incorrect then set                       
            //valid_cmd to false
            out = 1;
            if(strcmp(token[num_tokens-2],"->") !=0){
                 valid_cmd = 1;
            }
            else{
                //set the outfile to the name of the file
                outfile = token[num_tokens-1];
            }

        }

        //Check to see if the first command is PP and make the path set to the
        //second command in the array then set find_path2 to the next command after        
        //the -> and put the next commands in to arg list if there are three
        //different pipes then keep do this process one more time
        if(strcmp(token[0],"PP") == 0){
            find_path[0] = token[1];
            while(strcmp(token[count],"->") != 0){
                 arg_val[count-1] = token[count];
                 count++;
            }
            if(strcmp(token[count],"->") != 0){
                 valid_cmd = 1;
            }
            pipe_true = 1;
            count++;
            s = 0;
            //only two pipes
            if (count_pipe < 2){
                find_path2[0] = token[count];
                while(count < num_tokens){
                     arg_val2[s] = token[count];
                     count++;
                     s++;
   
                }
            }else{ //three pipes
                find_path2[0] = token[count];                                                      
                while(strcmp(token[count],"->") != 0){
                    arg_val2[s] = token[count];                                                        
                    count++;
                    s++;
                }
                count++;
                s = 0;
                find_path3[0] = token[count];
                while(count < num_tokens){
                    arg_val3[s] = token[count];
                    count++;
                    s++;
                }
           }

        }
        //for the first command (if there are two different) add the command
        //to the path of each part of the array made from the rc and check
        //if this path exists using stat() if so then set the cmd_path to this
        //path
        for (int j=0;j<lines;j++){
            if (out != 1 && pipe_true != 1){
                memset(find_path,0,sizeof find_path);
                find_path[0] = token[0];
                arg_val[j] = token[j];
            }
            strcat(temp[j],find_path[0]);
            if (stat(temp[j],&buffer) == 0){
                cmd_path = temp[j];

            }
        }


        //if this is a piped command then we also need to do this for the second
        //command so we need to reset the temp array to the old paths and then
        //we need to check each of the paths with the new command to find the other        
        //path and set cmd_path2 to this path if there are three pipes then
        //repeat this again with the last set of commands                                  
        if(pipe_true  == 1){
            memset(temp2,0,sizeof temp);                                                       
            for(int l=0;l<lines;l++){
                m = 0;                                                                             
                strcat(temp2[l],path[l]);
                while(temp2[l][m] != '\n'){
                    m++;
                }
                if (temp2[l][m-1] != '/'){
                        temp2[l][m] = '/';
                        temp2[l][m+1] = '\0';
                }else{
                        temp2[l][m] = '\0';
                }
            }

            for(int k=0;k<lines;k++){
                strcat(temp2[k],find_path2[0]);
                if (stat(temp2[k],&buffer) == 0){
                    cmd_path2 = temp2[k];
                }
            }

            if(count_pipe >= 2){ //three pipes
                memset(temp3,0,sizeof temp3);
                for(int w=0;w<lines;w++){

                    m = 0;
                    strcat(temp3[w],path[w]);
                    while(temp3[w][m] != '\n'){
                        m++;
                    }
              
                    if (temp3[W][m-1] != '/'){ //format correctly
                        temp3[W][m] = '/';
                        temp3[W][m+1] = '\0';
                    }else{
                        temp3[W][m] = '\0';
                    }
                }

                for(int p=0;p<lines;p++){                                                              
                    strcat(temp3[p],find_path3[0]);
                    if (stat(temp3[p],&buffer) == 0){                                                      
                        cmd_path3 = temp3[p];
                    }
                }
            }

        }
        //if the cmd_path could not be found or the command is not valid then set
        //the valid comand to false and print out an error message
        if (pipe_true == 1){
            if(count_pipe >= 2){
                if (cmd_path == NULL || cmd_path2 == NULL || cmd_path3 == NULL){
                    fprintf(stderr, "Invalid command, path could not be found\n");                     
                    valid_cmd = 1;
                }
            }else {
                if (cmd_path == NULL || cmd_path2 == NULL){
                    fprintf(stderr, "Invalid command, path could not be found\n");
                    valid_cmd = 1;
                }
            }

        }else{
            if (cmd_path == NULL|| valid_cmd == 1){
                fprintf(stderr,"Invalid command, path could not be found\n");
                valid_cmd = 1;
            }
        }

        line_len = strlen(input);
        
        //if this is a valid command and is not piped or outfiled then create the          
        //child process and run exeve with the command
        //This section of code was created in reference to appendix b,c,d
        if (valid_cmd == 0 && out == 0 && pipe_true == 0){
                if ((pid = fork()) == 0){
                        execve(cmd_path,arg_val,envp);                                             
                }
        //If it is a valid command and is outfiled then we need to create the child        
        //process and open or create the desired file, if the file can not be
        //opened then create a error message, redirect the stdout and error to this        
        //file and then run execve with the command
        }else if(valid_cmd == 0 && out == 1 && pipe_true == 0){
                if((pid = fork()) == 0){
                    fd1 = open(outfile, O_CREAT|O_RDWR, S_IRUSR|S_IWUSR);
                    if (fd1 == -1){
                        fprintf(stderr, "Cannot open %s for writing\n",outfile);
                        exit(1);
                    }
                    dup2(fd1,1);
                    dup2(fd1,2);
                    execve(cmd_path,arg_val,envp);
                }
        //Lastly if this is a valid command and is piped then we need to create the        
        //pipe first, then the child head is created which directs the stdout into
        //fd[1] and closes fd[0] and then runs the first command of the pipe, the
        //second part is to then create the child process and direct the stdin into        
        //fd[0] close fd[1] and run the second command in the pipe
        }else if(valid_cmd == 0 && pipe_true == 1 && count_pipe < 2){
                pipe(fd);
                if((pid_head = fork()) == 0){
                    dup2(fd[1], 1);
                    close(fd[0]);
                    execve(cmd_path, arg_val, envp);
                }

                if ((pid_tail = fork()) == 0) {
                    dup2(fd[0], 0);
                    close(fd[1]);
                    execve(cmd_path2, arg_val2, envp);
                }
        /*
        The last case is if there are three pipe commands I created this code
        with the help of https://stackoverflow.com/questions/28732195/c-cant-pipe-three-processes
        to help with some of the logic of using two pipes. This code first
        creates the first fd pipe and child and redirects the stdout of this
        child to the to fd[1] in the pipe and runs the first command after this
        the second pipe is created and so is the second child which takes the stdin        
        into fd[0] and then writes the stdout to the second fd2[1] pipe after
        and then runs the second command closing all used pipes then the last
        child is created which takes stdin and puts this into fd2[0] this last
        child runs the third command and the piping is finished */

        }else if(valid_cmd == 0 && pipe_true == 1 && count_pipe >= 2){
                pipe(fd);
                if((pid_head = fork()) == 0){
                    dup2(fd[1], 1);
                    close(fd[1]);
                    execve(cmd_path, arg_val, envp);
                }

                close(fd[1]);
                pipe(fd2);
                if((pid_middle = fork()) == 0){
                    dup2(fd[0], 0);
                    close(fd[0]);

                    dup2(fd2[1],1);
                    close(fd2[1]);
                    execve(cmd_path2, arg_val2, envp);
                }
                close(fd[0]);
                close(fd2[1]);

                if ((pid_tail = fork()) == 0) {
                    dup2(fd2[0], 0);
                    close(fd2[0]);
                    execve(cmd_path3, arg_val3, envp);
                }
        }

       //if we have not run a pipe then we can just wait for the one child process
        if(pipe_true  == 0 && valid_cmd == 0){
                waitpid(pid, &status, 0);
        //Otherwise we need to close the pipe in the parent and wait for the two           
        //child processes
        }else if (count_pipe < 2 && valid_cmd == 0){
                close(fd[0]);
                close(fd[1]);
                waitpid(pid_head, &status,0);                                                      
                waitpid(pid_tail, &status,0);
        //Or if there are three commands we have to wait for the three children
        //processes to complete and close the two pipes in the parent process
        }else if (count_pipe >= 2 && valid_cmd == 0){
                close(fd[0]);
                close(fd[1]);
                close(fd2[0]);
                close(fd2[1]);
                waitpid(pid_head, &status,0);
                waitpid(pid_middle, &status, 0);
                waitpid(pid_tail, &status,0);
        }
    }

        //have to close the rc file
        fclose(fp);
        return 0;
}