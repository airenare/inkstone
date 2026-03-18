---
tags:
  - blog
---

# A Simple Trick for Resetting SSH Keys When Swapping Raspberry Pi Devices

If you’ve worked with Raspberry Pi boards for a while, you’ve probably run into this problem: you switch out a Pi or reflash the SD card, and suddenly, SSH refuses to connect. Instead, you’re greeted with a warning about the remote host key changing. It’s not exactly a showstopper, but it’s definitely annoying—especially when you’re just trying to quickly tinker with your setup.

The issue happens because SSH keeps a record of the fingerprint (or “host key”) for every device you connect to in a file called `known_hosts`. When you reuse the same IP address or hostname for a different Pi (or a freshly re-imaged one), SSH gets confused. The new device has a different fingerprint, and SSH assumes something suspicious might be going on—rightfully so, from a security perspective.

## The Annoying Part for Raspberry Pi Tinkerers

Let’s say you’re swapping Pis regularly—maybe one is a media server, another is for experiments, or you’re just switching OS images. Every time you do this, SSH will stop you with something like:

```bash
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

To fix it, you have to dig into `~/.ssh/known_hosts`, find the line with the old IP or hostname, and delete it. It works, but after a few times, this manual fix gets old.

## Automating the Fix with a Simple `zsh` Function

I got tired of the repetition and wanted something quicker. So, I wrote a small function for `zsh` to streamline the process: it automatically removes the old SSH key for the given IP or hostname and then attempts a new connection.

Here’s the function, which I named `ssh_reset`:

```bash
function ssh_reset() {
    local host=$1
    local ip_address=$(echo $host | awk -F'@' '{print $2}')
    ssh-keygen -R "$ip_address"
    ssh "$host"
}
```

## What It Does:
1. **Removes the old SSH key**: It uses `ssh-keygen -R` to remove the existing key for the specified IP address or hostname from your `known_hosts` file.
2. **Connects via SSH**: After cleaning up the old key, it attempts a new SSH connection, prompting you to accept the fresh host key for the new device.

## Setting It Up

Here’s how to add it to your terminal workflow:

1. Open your `.zshrc` file:
   ```bash
   nano ~/.zshrc
   ```

2. Paste the function at the bottom of the file.

3. Reload your `.zshrc`:
   ```bash
   source ~/.zshrc
   ```

That’s it! Now, you can use the `ssh_reset` command like this:

```bash
ssh_reset pi@192.168.1.100
```

This will automatically reset the SSH key for the Pi at `192.168.1.100` and attempt a new connection to `pi@192.168.1.100`. No more hunting through `known_hosts` manually.

## Why This is Handy

This trick won’t save the world, but if you’re regularly juggling Raspberry Pi setups, it can definitely save a few minutes (and a bit of frustration). No more interrupting your workflow to fix host key issues—just reset and go.

If you’re like me and enjoy hopping between different Pi configurations, this little `ssh_reset` function might just become one of your favorite shortcuts. Give it a try, and let me know if it makes life a little easier for you too!


