/*
 * Copyright 2016-2018 Mikkel Strange, Fawzi Mohamed
 * 
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

package eu.nomad_lab.parsers

import eu.{ nomad_lab => lab }
import eu.nomad_lab.DefaultPythonInterpreter
import org.{ json4s => jn }
import scala.collection.breakOut
import java.nio.charset.StandardCharsets

object AtkParser extends SimpleExternalParserGenerator(
  name = "AtkParser",
  parserInfo = jn.JObject(
    ("name" -> jn.JString("AtkParser")) ::
      ("parserId" -> jn.JString("AtkParser" + lab.AtkVersionInfo.version)) ::
      ("versionInfo" -> jn.JObject(
        ("nomadCoreVersion" -> jn.JObject(lab.NomadCoreVersionInfo.toMap.map {
          case (k, v) => k -> jn.JString(v.toString)
        }(breakOut): List[(String, jn.JString)])) ::
          (lab.AtkVersionInfo.toMap.map {
            case (key, value) =>
              (key -> jn.JString(value.toString))
          }(breakOut): List[(String, jn.JString)])
      )) :: Nil
  ),
  mainFileTypes = Seq("application/x-netcdf"),
  cmd = Seq(DefaultPythonInterpreter.pythonExe(), "${envDir}/parsers/atk/parser/parser-atk/parser_atk.py",
    "${mainFilePath}"),
  mainFileRe = "".r,
  resList = Seq(
    "parser-atk/atkio.py",
    "parser-atk/configurations.py",
    "parser-atk/libxc_names.py",
    "parser-atk/parser_atk.py",
    "parser-atk/parser_calculator.py",
    "parser-atk/parser_configurations.py",
    "parser-atk/periodic_table.py",
    "parser-atk/physical_quantities.py",
    "parser-atk/setup_paths.py",
    "nomad_meta_info/public.nomadmetainfo.json",
    "nomad_meta_info/common.nomadmetainfo.json",
    "nomad_meta_info/meta_types.nomadmetainfo.json",
    "nomad_meta_info/atk.nomadmetainfo.json"
  ) ++ DefaultPythonInterpreter.commonFiles(),
  dirMap = Map(
    "parser-atk" -> "parsers/atk/parser/parser-atk",
    "nomad_meta_info" -> "nomad-meta-info/meta_info/nomad_meta_info"
  ) ++ DefaultPythonInterpreter.commonDirMapping(),
  metaInfoEnv = Some(lab.meta.KnownMetaInfoEnvs.atk)
) {
  override def isMainFile(filePath: String, bytePrefix: Array[Byte], stringPrefix: Option[String]): Option[ParserMatch] = {
    // TO DO: be more specific: open and look for something special, not all netcdf files are Atk files...
    if (bytePrefix.startsWith("CDF".getBytes(StandardCharsets.US_ASCII)) &&
      bytePrefix.size > 3 && (bytePrefix(3) == 1 || bytePrefix(3) == 2))
      Some(ParserMatch(mainFileMatchPriority, mainFileMatchWeak))
    else
      None
  }
}
