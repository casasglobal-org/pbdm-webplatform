#!/usr/bin/perl -w
# Script that plots overall raster statistics 
# using gnuplot and puts .png outputs in a HTML page
# Author: Luigi Ponti
# Date: 20 September 2006

# Read Directory where maps are saved and 
# other parameters from script arguments.
my $SaveDir=$ARGV[0];
my $LegendString=$ARGV[1];

# Read string from GRASS parser.
chdir ($SaveDir);
my $file ="$LegendString-PLOTb.html";
open (OUT, ">$LegendString-PLOTb.html") or die "Can't open $LegendString-PLOTb.html for writing: $!";

# Begin HTML page.
print OUT '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">';
print OUT "\n";
print OUT "<html>";
print OUT "\n";
print OUT "<head>";
print OUT "\n";
print OUT "<title>$LegendString - Total Plots</title>";
print OUT "\n";
print OUT '<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" >';
print OUT "\n";
print OUT '</head>';
print OUT "\n";
print OUT '<body>';

print OUT "\n<h1>Barchart statistics for \"$LegendString\"</h1>";

opendir(DIR, $SaveDir) || die "can't opendir $SaveDir: $!";

# Loop to plot data with gnuplot
# and save them to .png images.
while (my $file = readdir(DIR))
{
	if ($file =~ /.\.tabTot/)
	{
		open (IN, "<$file") or die "Can't open $file for reading: $!";
		$file =~ s/\.tabTot//;	
		# open pipe to gnuplot and set terminal type
		open(GNUPLOT, "|gnuplot") || die "can't find gnuplot";
		print GNUPLOT "set term png enhanced font \"C:/cygwin/home/andy/Arial.ttf\" 10 size 640,480 xffffff\n";
		print GNUPLOT "set size 0.4,0.5\n";
		print GNUPLOT "set out \"$file-PLOTb.png\"\n";
		print GNUPLOT "set autoscale\n";
		print GNUPLOT "set xrange [ 0:5 ]\n";
		print GNUPLOT "set tics out\n";
		print GNUPLOT "set xtics nomirror rotate by 90 (\"Low\" 1, \"Mid-low\" 2, \"Mid-high\" 3, \"High\" 4)\n";
		print GNUPLOT "set ytics nomirror\n";
		print GNUPLOT "set title \"Extent of raster categories\"\n";
		print GNUPLOT "set ylabel \"Area (km^{2})\" 0,-3\n";
		print GNUPLOT "unset key\n";
		print GNUPLOT "set boxwidth 0.5 absolute\n";
		print GNUPLOT "set style fill solid 0.5 border\n";
		print GNUPLOT "plot \"$file.tabTot\"\\\n";
		print GNUPLOT "using (\$1*1):(\$2/(10**6)) title \"Low\" with boxes linetype -1,\\\n";
		print GNUPLOT "\"$file.tabTot\"\\\n";
		print GNUPLOT "using (\$1*2):(\$3/(10**6)) title \"Mid-Low\" with boxes linetype -1,\\\n";
		print GNUPLOT "\"$file.tabTot\"\\\n";
		print GNUPLOT "using (\$1*3):(\$4/(10**6)) title \"Mid-High\" with boxes linetype -1,\\\n";
		print GNUPLOT "\"$file.tabTot\"\\\n";
		print GNUPLOT "using (\$1*4):(\$5/(10**6)) title \"High\" with boxes linetype -1\n";
		print GNUPLOT "set out\n";

		print OUT "Plot for input file <b>$file.txt</b><br>\n";
		print OUT "<img src=\"$file-PLOTb.png\">\n";
		print OUT "<hr>\n";
		close IN;
	}
}

print OUT '</body>';
print OUT '</html>';
close OUT;
close GNUPLOT;
closedir DIR;
