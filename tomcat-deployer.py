import os
import shutil
import subprocess
import time
import logger

SLEEP_SECONDS = 3


class TomcatDeployer(object):
    def __init__(self, catalina_home, source_dir, backup_dir, war_file_name):
        self.catalina_home = catalina_home
        self.source_dir = source_dir
        self.backup_dir = backup_dir
        self.war_file_name = war_file_name

    def get_webapps_dir(self):
        return "%s/webapps" % self.catalina_home

    def get_startup_sh(self):
        return "%s/bin/startup.sh" % self.catalina_home

    def get_shutdown_sh(self):
        return "%s/bin/shutdown.sh" % self.catalina_home

    def start_tomcat(self):
        logger.info("Starting Tomcat...")
        sh = self.get_startup_sh()
        subprocess.call([sh])

    def stop_tomcat(self):
        logger.info("Stopping Tomcat...")
        sh = self.get_shutdown_sh()
        subprocess.call([sh])

    def backup_file(self):
        source = "%s/%s.war" % (self.get_webapps_dir(), self.war_file_name)
        dest = "%s/%s_%s.war" % (self.backup_dir, self.war_file_name, time.strftime("%Y%m%d%H%M%S"))

        logger.info("cp %s %s" % (source, dest))
        shutil.copy(source, dest)

    def copy_file(self):
        source = "%s/%s.war" % (self.source_dir, self.war_file_name)
        dest = "%s/%s.war" % (self.get_webapps_dir(), self.war_file_name)

        logger.info("cp %s %s" % (source, dest))
        shutil.copy(source, dest)

    def clear_webapps_directory(self):
        webapps_dir = self.get_webapps_dir()

        logger.info("rm -rf %s" % webapps_dir)
        if os.path.exists(webapps_dir):
            shutil.rmtree(webapps_dir, True)

        logger.info("mkdir %s" % webapps_dir)
        if not os.path.exists(webapps_dir):
            os.makedirs(webapps_dir)

    def deploy(self):
        logger.info("Deploying...")

        self.backup_file()
        self.stop_tomcat()
        time.sleep(2)

        self.clear_webapps_directory()
        self.copy_file()
        self.start_tomcat()

        logger.info("Done.")


class FileWatcher(object):
    def __init__(self, watch_file, deployer):
        self.watch_file = watch_file
        self.deployer = deployer

    def get_last_modified(self):
        return os.stat(self.watch_file).st_atime

    def watch(self):
        last_modified = self.get_last_modified()
        just_updated = False
        logger.info("Waiting for Changes...")

        while True:
            time.sleep(SLEEP_SECONDS)
            new_last_modified = self.get_last_modified()

            was_updated = False
            if new_last_modified != last_modified:
                logger.info("File was updated.")
                was_updated = True

            if not was_updated and just_updated:
                logger.info("File has stopped changing. Deploying.")
                self.deployer.deploy()
                new_last_modified = self.get_last_modified()

            just_updated = was_updated
            last_modified = new_last_modified


def continuous_deploy():
    deployer = TomcatDeployer("./tomcat", "source", "backup", "ROOT")
    watcher = FileWatcher("source/ROOT.war", deployer)
    watcher.watch()


if __name__ == "__main__":
    continuous_deploy()
