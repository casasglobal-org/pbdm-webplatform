#!/usr/bin/perl -w
# Script that plots raster statistics by ecozones 
# using gnuplot and puts .png outputs in a HTML page
# Author: Luigi Ponti
# Date: 19 September 2006

# Read Directory where maps are saved and 
# other parameters from script arguments.
my $SaveDir=$ARGV[0];
my $LegendString=$ARGV[1];

# Read string from GRASS parser.
chdir ($SaveDir);
my $file ="$LegendString-PLOTa.html";
open (OUT, ">$LegendString-PLOTa.html") or die "Can't open $LegendString-PLOTa.html for writing: $!";

# Begin HTML page.
print OUT '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">';
print OUT "\n";
print OUT "<html>";
print OUT "\n";
print OUT "<head>";
print OUT "\n";
print OUT "<title>$LegendString - Zoned Plots</title>";
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
	if ($file =~ /.\.tab$/)
	{
		open (IN, "<$file") or die "Can't open $file for reading: $!";
		$file =~ s/\.tab//;
		# open pipe to gnuplot and set terminal type
		open(GNUPLOT, "|gnuplot") || die "can't find gnuplot";
		print GNUPLOT "set term png enhanced font \"C:/cygwin/home/andy/Arial.ttf\" 10 size 640,480 xffffff\n";
		print GNUPLOT "set size 1.5,1.0\n";
		print GNUPLOT "set out \"$file-PLOTa.png\"\n";
		print GNUPLOT "set autoscale\n";
		print GNUPLOT "set xrange [ 0.5:18.5 ]\n";
		print GNUPLOT "set tics out\n";
		print GNUPLOT "set xtics nomirror 1,1,18\n";
		print GNUPLOT "set mxtics 2\n";
		print GNUPLOT "set ytics auto\n";
		print GNUPLOT "set title \"Extent of raster categories by evapotranspiration zones\"\n";
		print GNUPLOT "set ylabel \"Area (km^{2})\" 0,-4\n";
		print GNUPLOT "set xlabel \"Evapotranspiration zones\"\n";
		print GNUPLOT "set key below Right width 1 height 0.5 box linewidth 0.5\n";
		print GNUPLOT "set boxwidth 0.2 absolute\n";
		print GNUPLOT "set style fill pattern border\n";
		print GNUPLOT "set grid mxtics ytics linewidth 2\n";
		print GNUPLOT "plot \"$file.tab\"\\\n";
		print GNUPLOT "using (\$1-0.3):(\$2/(10**6)) title \"Low\" with boxes linetype -1,\\\n";
		print GNUPLOT "\"$file.tab\"\\\n";
		print GNUPLOT "using (\$1-0.1):(\$3/(10**6)) title \"Mid-Low\" with boxes linetype -1,\\\n";
		print GNUPLOT "\"$file.tab\"\\\n";
		print GNUPLOT "using (\$1+0.1):(\$4/(10**6)) title \"Mid-High\" with boxes linetype -1,\\\n";
		print GNUPLOT "\"$file.tab\"\\\n";
		print GNUPLOT "using (\$1+0.3):(\$5/(10**6)) title \"High\" with boxes linetype -1\n";
		print GNUPLOT "set out\n";
		
		print OUT "Plot for input file <b>$file.txt</b><br>\n";
		print OUT "<img src=\"$file-PLOTa.png\">\n";
		print OUT "<hr>\n";
		close IN;
	}
}

print OUT '</body>';
print OUT '</html>';
close OUT;
close GNUPLOT;
closedir DIR;
