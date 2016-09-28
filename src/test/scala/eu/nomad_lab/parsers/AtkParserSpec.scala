package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object AtkParserSpec extends Specification {
  "AtkParserTest" >> {
    "test Si2 with json-events" >> {
      ParserRun.parse(AtkParser, "parsers/atk/test/examples/Si2.nc", "json-events") must_== ParseResult.ParseSuccess
    }
    "test Si2 with json" >> {
      ParserRun.parse(AtkParser, "parsers/atk/test/examples/Si2.nc", "json") must_== ParseResult.ParseSuccess
    }
    "test Water with json-events" >> {
      ParserRun.parse(AtkParser, "parsers/atk/test/examples/Water.nc", "json-events") must_== ParseResult.ParseSuccess
    }
    "test Water with json" >> {
      ParserRun.parse(AtkParser, "parsers/atk/test/examples/Water.nc", "json") must_== ParseResult.ParseSuccess
    }
  }
}
