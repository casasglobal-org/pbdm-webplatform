#!/usr/bin/perl -w
# Script that plots histograms produced by  
# d.histogram and puts .png outputs in a HTML page
# Author: Luigi Ponti
# Date: 16 January 2008

# Read Directory where maps are saved and 
# other parameters from script arguments.
my $SaveDir=$ARGV[0];
my $LegendString=$ARGV[1];

# Read string from GRASS parser.
chdir ($SaveDir);
my $file ="$LegendString-PLOTc.html";
open (OUT, ">$LegendString-PLOTc.html") or die "Can't open $LegendString-PLOTc.html for writing: $!";

# Begin HTML page.
print OUT '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">';
print OUT "\n";
print OUT "<html>";
print OUT "\n";
print OUT "<head>";
print OUT "\n";
print OUT "<title>$LegendString - Histograms</title>";
print OUT "\n";
print OUT '<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" >';
print OUT "\n";
print OUT '</head>';
print OUT "\n";
print OUT '<body>';

print OUT "\n<h1>Histograms for \"$LegendString\"</h1>";

opendir(DIR, $SaveDir) || die "can't opendir $SaveDir: $!";

# Loop write plot info.
while (my $file = readdir(DIR))
{
	if ($file =~ /.-HIST\.png/)
	{
		open (IN, "<$file") or die "Can't open $file for reading: $!";
		print OUT "Histogram for input file <b>$file.txt</b><br>\n";
		print OUT "<img src=\"$file\" width=\"66%\">\n";
		print OUT "<hr>\n";
		close IN;
	}
}

print OUT '</body>';
print OUT '</html>';
close OUT;
closedir DIR;
