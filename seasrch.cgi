#/usr/bin/perl

#seasrch.cgi
##################
## cgi-скрипт для поиска данных в таблицах
##################

use CGI qw(:standard escapeHTML);
use DBI;
use strict;


our $LIMIT = 100; # максимальное количество строк в таблице


my $search = param('search') || ''; # получение значения search

my @arr_html;						#массив для накопления строк html

my $top_html = &top_html(); 		# заголовок страницы

$top_html =~ s/%%search%%/$search/;	# вставка значения search в html

print $top_html;


# имя базы данных
my $dbname = "volk";
# имя пользователя
my $username = "postgres";
# пароль
my $password = "1";
# имя или IP адрес сервера
my $dbhost = "localhost";
# порт
my $dbport = "5432";
# опции
my $dboptions = "-e";
# терминал
my $dbtty = "ansi";

my $dbh = DBI->connect("dbi:Pg:dbname=$dbname;options=$dboptions;tty=$dbtty","$username","$password",
		    {PrintError => 0});

if ($DBI::err != 0) {
  print $DBI::errstr . "\n";
  exit($DBI::err);
}



if ($search ne ''){
	$search = escapeHTML($search);
	$search =~ s/'/''/;
	my $LIMIT1 = $LIMIT +1;
	{
		### поиск адреса в таблице message по регулярному выражению
		my $query_messages = qq/SELECT created, str FROM message WHERE str ~ '<= $search ' ORDER BY int_id LIMIT $LIMIT1/;
		my $sth = $dbh->prepare($query_messages);
		$sth->execute();
		my $arr = $sth->fetchall_arrayref();
		my @arr_rows = @$arr;
		
		print incoming_messages();
		print &begin_table();
		
		my $overflow = $#arr_rows >= $LIMIT;
		pop @arr_rows;
		### вывод строк таблицы
		for my $row (@arr_rows){
			my $timestamp = $row->[0];
			my $str = $row->[1];
			my $s = &row_html();
			$s =~ s/%%timestamp%%/$timestamp/;
			$s =~ s/%%str%%/$str/;
			print $s;
		}
		print &end_table();
		if ($overflow){
			print "<p>количество найденных строк превышает $LIMIT/p>";
			
		}
	}
	{
		### поиск адреса в таблице log по значению address
		my $query_log = qq/SELECT created, str FROM log WHERE address = '$search' ORDER BY int_id LIMIT $LIMIT1/;
		my $sth = $dbh->prepare($query_log);
		$sth->execute();
		
		my $arr = $sth->fetchall_arrayref();
		my @arr_rows = @$arr;
		
		print other_messages();
		print &begin_table();
		
		my $overflow = $#arr_rows >= $LIMIT;
		pop @arr_rows;
		
		### вывод строк таблицы
		for my $row (@arr_rows){
			my $timestamp = $row->[0];
			my $str = $row->[1];
			my $s = &row_html();
			$s =~ s/%%timestamp%%/$timestamp/;
			$s =~ s/%%str%%/$str/;
			print $s;
		}
		print &end_table();
		if ($overflow){
			print "<p>количество найденных строк превышает $LIMIT/p>";
			
		}
	}
}

print &bottom_html();

$dbh->disconnect();



sub top_html()
{ 
	return q{<!DOCTYPE html>

<html lang="ru">
<head>
<meta charset="UTF-8">
<title> Таблица записей почтового журнала </title>
</head>
<body>
<p><H1>Таблица записей почтового журнала</H1></p>
<p>&nbsp;</p>
<form method="GET">
<p>Поиск&nbsp;<input type="text" name="search" value="%%search%%" ACTION="/cgi-bin/search.cgi" /> <input type="submit" value="Search" /></p>
</form>
	};
}

sub bottom_html{
	return q{
</body>
</html>
	};
}

sub incoming_messages{
	return q{<p><H2>Входящие сообщения</H2></p>
	};
}
sub other_messages{
	return q{<p><H2>Другие сообщения</H2></p>
	};
}

sub begin_table{
	return q{<table style="border-collapse: collapse; width: 100%;" border="2">
 <tbody>
<tr>
<td style="width: 10%;" align="center"><b>timestamp</b></td>
<td style="width: 90%;" align="center"><b>Строка лога<b></td>
</tr>
	};
}

sub row_html{
	return q{<tr>
<td align="center">%%timestamp%%</td>
<td >%%str%%</td>
</tr>
	};
}

sub end_table{
	return q{
</tbody>
</table>
	};
}

1;


