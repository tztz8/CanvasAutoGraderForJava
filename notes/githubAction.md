# GitHub Action

```yaml
#name: Junit test and Checkstyle
name: test

on: [ push ]

jobs:
  buildAndTest:

    runs-on: ubuntu-latest
    timeout-minutes: 3

    permissions:
      contents: read
      checks: write
      id-token: write

    # ##########################
    # # CHANGE THESE VARIABLES #
    # ##########################
    env:
      # tests jar file path
      Junit_Test_Jar_File: lab3/cscd212-s23-lab3-sol-tests.jar
      # the class that has the tests
      Junit_Class_To_run: cscd211tests.lab3.CSCD212Lab3Test
      # the date to auto fail (if today >= deadline then fail)
      # NOTE: need .autotests/jar/deadLine.jar
      Dead_Line: 04-16-2023


    steps:
      # # Setup #
      
      # Get 
      - name: Geting the github project
        uses: actions/checkout@v3
      - name: Getting our tools and tests
        uses: actions/checkout@v3
        with:
          repository: 'EWU-CSCD212/cscd212-s23-jar-tests-files'
          path: 'tools'
          ref: main
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'adopt'

      - name: Get Junit Launcher
        run: wget https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.9.2/junit-platform-console-standalone-1.9.2.jar
      - name: Build Code for testing
        run: javac -Xlint:unchecked -cp junit-platform-console-standalone-1.9.2.jar -cp tools/${{ env.Junit_Test_Jar_File }} -d out/classes $(find src -name '*.java')
      - name: Run junit test (${{ env.Junit_Class_To_run }})
        run: java -jar junit-platform-console-standalone-1.9.2.jar --reports-dir=build/test-results/test1 -cp tools/${{ env.Junit_Test_Jar_File }} -cp out/classes --select-class=${{ env.Junit_Class_To_run }}

      # Test deadline
      - name: check deadline
        if: always()
        run: java -jar tools/tools/deadLine.jar ${{ env.Dead_Line }}

      # post the junit test results
      - name: Publish Test Report
        uses: mikepenz/action-junit-report@v3
        if: always()
        with:
          report_paths: '**/build/test-results/test*/TEST*.xml'
          # so the results can be used in other actions
#      - name: Upload Test Report to artifact
#        uses: actions/upload-artifact@v3
#        if: always() # always run even if the previous step fails
#        with:
#          name: junit-test-results
#          path: '**/build/test-results/test*/TEST-*.xml'
#          retention-days: 1
      - name: Remove tests so not include in Checkstyle
        if: always()
        run: rm -fr tests
      # run and post the checkstyle test
      - name: Run check style info
        uses: nikitasavinov/checkstyle-action@master
        if: always() # always run even if the previous step fails
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          reporter: 'github-check'
          level: info
          tool_name: 'reviewdog-info'
          #checkstyle_config: https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212.xml
          checkstyle_config: https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-info.xml
      - name: Run check style warning
        uses: nikitasavinov/checkstyle-action@master
        if: always() # always run even if the previous step fails
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          reporter: 'github-check'
          level: warning
          tool_name: 'reviewdog-warning'
          #checkstyle_config: https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212.xml
          checkstyle_config: https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-warning.xml
      - name: Run check style error
        uses: nikitasavinov/checkstyle-action@master
        if: always() # always run even if the previous step fails
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          reporter: 'github-check'
          level: error
          tool_name: 'reviewdog-error'
          #checkstyle_config: https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212.xml
          checkstyle_config: https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml
#      - uses: dbelyaev/action-checkstyle@v0.7.4
#        if: always() # always run even if the previous step fails
#        with:
#          checkstyle_config: https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml
#          filter_mode: nofilter
#          github_token: ${{ secrets.github_token }}
#          level: error

```