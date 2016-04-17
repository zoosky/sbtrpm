name := "appname"
version := "1.0"

// donte package Scala Library
autoScalaLibrary := false

//rpm
import com.typesafe.sbt.packager.archetypes.ServerLoader
enablePlugins(JavaServerAppPackaging, RpmPlugin)
serverLoading in Rpm := ServerLoader.Systemd
rpmVendor := "zoosky"
rpmLicense := Option("none")


import NativePackagerHelper._
mappings in Universal ++= contentOf("src/resources")
// this does the same:
//mappings in Universal <++= sourceDirectory map (src => contentOf(src / "resources"))

//For static content it can be added to mappings directly, including the directory `doc`
mappings in Universal ++= directory("doc")
