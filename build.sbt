name := "appname"
version := "1.0"


//rpm
import com.typesafe.sbt.packager.archetypes.ServerLoader
enablePlugins(JavaServerAppPackaging, RpmPlugin)
serverLoading in Rpm := ServerLoader.Systemd
rpmVendor := "zoosky"
rpmLicense := Option("none")

