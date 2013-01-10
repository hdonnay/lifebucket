======================
The Bad Query Language
======================

The Bad Query Language is the way to extract data for graphing. In
`lifebucket` terms, it's a lens.

It works like this:

    START;END;LAMBDA

START
  Start is a timestamp to start searching at, **or** a number of days
  followed by a `d` to denote days.

      00000000;END;LAMBDA
      5d;;LAMBDA

END
  A timestamp to stop searching. If magic string `now`, a current
  timestamp is calculated and used. If the START argument was relative,
  this argument will be discarded

      START;now;LAMBDA
      5d;;LAMBDA

LAMBDA
  A python lambda used to filter results. The json module is loaded into
  this environment.

      5d;;lambda x: return x
      7d;;lambda x: return json.loads(x)['weight']


Some future implementation ideas:

 #. have workers that periodically run on a copy of the production db to
    migrate a lens' data into dbs just for them. This would make requesting
    data as easy as serializing a db, and python's json would take care of
    sequencing it for us. Would hurt the resolution on data retrival.

    * That could be overcome by keeping metadata on the latest checked
      timestamp and only mapping new data since then.

 #. Could determing if a piece of data belongs in a lens-specific database
    at insert-time.

    * Would make databases less portable. would have to import data after
      importing lenses, and through a custom function.

    * Makes data insertion O(n) with number of lenses.
