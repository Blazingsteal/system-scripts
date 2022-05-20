PERSONAL=/home/martin/.gitconfig-personal
PROFESSIONAL=/home/martin/.gitconfig-professional
GITCONFIG=/home/martin/.gitconfig

message() {
    echo "$1"
}

personal() {
    message "Switching to personal gitconfig"
    message "Executing command: cp $PERSONAL $GITCONFIG"
    cp $PERSONAL $GITCONFIG
    exit_code=$?
    if [ $exit_code = 0 ]; then
        message "Swap Successful!"
    else
        message "Error swapping gitconfig code: $exit_code"
    fi
    sync
}

professional() {
    message "Switching to professional gitconfig"
    message "Executing command: cp $PROFESSIONAL $GITCONFIG"
    cp $PROFESSIONAL $GITCONFIG
    exit_code=$?
    if [ $exit_code = 0 ]; then
        message "Swap Successful!"
    else
        message "Error swapping gitconfig code: $exit_code"
    fi
    sync
}

message "-------------------------"
message "GIT CONFIG SWAPPER SCRIPT"
message "-------------------------"
message "DATE: $(date)"

if [ "$1" = "pro" ]; then
    professional
elif [ "$1" = "personal" ]; then
    personal
else
    message "Unsupported argument: $1"
fi
