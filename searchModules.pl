#!/usr/bin/perl
$mods = "";
$fileToRead = $ARGV[0];
open F, "<", $fileToRead or die "Failed to open webpage: $!"; 
while ($line = <F>) {
    unless ($line =~ /\#/) {
        if ($line =~ /^.*from\s(\w+)\simport.*/) {
            $line =~ s/^.*from\s(\w+)\simport.*/$1/;
            # print("Matched from import:  $line\n");
            $mods = $mods . $line;
        } elsif ($line =~ /^.*import (\w+)/) {
            $line =~ s/^.*import (\w+)/$1/;
            # print("Matched import only: $line\n");
            $mods = $mods . $line ;
        }
    # print("Mods currently: $mods\n");
    }
}
close F;
chomp $mods;
# print("Final: $mods");
print($mods);

unless(open FILE, '>', 'requirements.txt') {
    die "\nUnable to create requirements.txt'\n";
}
print FILE $mods;
close FILE;


# $envPath = $ARGV[1] . "/bin/activate";
# system("source $envPath");
$installCmd = "pip install -r requirements.txt"; 
system($installCmd);

