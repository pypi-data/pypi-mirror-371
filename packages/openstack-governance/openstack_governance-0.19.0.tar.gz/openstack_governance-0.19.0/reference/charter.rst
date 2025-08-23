=======================================
 OpenStack Technical Committee Charter
=======================================

Mission
=======

The Technical Committee ("TC") is tasked with providing the technical
leadership for OpenStack as a whole (all official projects, as defined below).
It enforces OpenStack ideals (Openness, Transparency, Commonality, Integration,
Quality...), decides on issues affecting multiple projects, forms an ultimate
appeals board for technical decisions, and generally has technical oversight
over all of OpenStack.

OpenStack Project Teams
=======================

OpenStack "Project Teams" are groups of people dedicated to the completion of
the OpenStack project mission, which is ''to produce a ubiquitous Open Source
Cloud Computing platform that is easy to use, simple to implement,
interoperable between deployments, works well at all scales, and meets
the needs of users and operators of both public and private clouds.''
Project Teams may create any code repository and produce any deliverable they
deem necessary to achieve their goals.

The work of project teams is performed under the oversight of the TC.
Contributing to one of their associated code repositories grants you
automatic AC status (see below). The TC has ultimate authority over
which project teams are designated as official OpenStack projects. The
projects are listed in :ref:`projects`.

Project Team Leads
==================

Project Team Leads ("PTLs") manage day-to-day operations, drive the team goals
and resolve technical disputes within their team. Each team
should be self-managing by the contributors, and all disputes should be
resolved through active debate and discussion by the community itself. However
if a given debate cannot be clearly resolved, the PTL can decide the outcome.
Although the TC is generally not involved in team-internal decisions, it
still has oversight over team decisions, especially when they
affect other teams or go contrary to general OpenStack goals.

TC Members
==========

The TC is composed of directly-elected members. It is partially renewed
using elections every 6 months. All TC members must be OpenStack Foundation
individual members. You can cumulate any other role, including Foundation
Director, with a TC seat.

TC Chair
========

After each election, the TC proposes one of its members to act as the TC chair.
In case of multiple candidates, it may use a single-winner election method to
decide the result (see below). The TC chair is responsible for making sure meetings
are held according to the rules described below, and for communicating the
decisions taken during those meetings to the Board of Directors and the
OpenStack community at large.

The elected TC chair will seek another TC member to volunteer to serve
as vice chair until the next chair election is held. The chair may delegate some regular
duties to the vice chair. In addition to any delegated tasks, the vice
chair is responsible for being ready to step in and fulfill the
responsibilities of the TC chair when the elected chair is not
available.

The term of the TC chair will continue until death, resignation, or removal,
the election of the next TC chair, or the TC chair ceases to be a TC member.
The current TC chair is in charge of the next TC chair election, and
stays in charge of TC chair duties until the next TC chair is elected.
The TC chair may be removed by the affirmative vote of at least half of
the total number of TC members.

Meeting
=======

The community should not wait for a formal meeting to raise issues or
bring questions to the Technical Committee (see
:doc:`/resolutions/superseded/20170425-drop-tc-weekly-meetings`). In most cases,
asynchronous communication via email or gerrit is preferred over
meetings. If a topic will require significant discussion or to need
input from members of the community other than the committee, start a
mailing list discussion on ``openstack-discuss at lists.openstack.org``
and use the subject tag ``[tc]`` to bring it to the attention of
Technical Committee members.

`TC status meetings <http://eavesdrop.openstack.org/#Technical_Committee_Meeting>`__
are public and held monthly in the
``#openstack-tc`` channel on the OFTC IRC network. The meeting
time is decided among TC members after each election. The TC maintains
an open list of candidate topics for the agenda on `the wiki
<https://wiki.openstack.org/wiki/Meetings/TechnicalCommittee>`__. Anyone
may add items to the list, and the chair or vice chair will set and
publicize the agenda before each meeting.

For a meeting to be actually held, at least half of the members need
to be present (rounded up: in a 13-member committee that means a
minimum of 7 people present). Non-members affected by a given
discussion are strongly encouraged to participate in the meeting and
voice their opinion, though only TC members can ultimately cast a
vote.

.. _charter-motions-section:

Motions
=======

Motions presented before the TC should be discussed publicly to give a chance to
the wider community to express their opinion. Motions should therefore be
announced on the development mailing list and posted to Gerrit for review for a
minimum of 7 calendar days.

TC members can vote positively, negatively, or abstain (using the
"RollCall-Vote" in Gerrit). Decisions need more positive votes than negative
votes (ties mean the motion is rejected), and a minimum of positive votes of at
least one third of the total number of TC members (rounded up: in a 13-member
committee that means a minimum of 5 approvers).

Patches with motions should use the gerrit topic tag ``formal-vote``.

Election for PTL seats
======================

PTL seats are completely renewed every development cycle. A separate election
is run for each project team. The election nomination as well as the voting
period should be open for at least fourteen days (2 or more weeks for each
phase). These elections are collectively held (from the nomination start
date until the voting end date) no later than 2 weeks prior to each cycle
final release date (on or before 'R-2' week)

If a PTL seat is vacated before the end of the cycle for which the individual
was elected or after the election (means leaderless project), the TC will
appoint a new PTL or move that project to the Distributed Project Leadership
model (see :doc:`/resolutions/20200803-distributed-project-leadership`),
in consultation with the outgoing PTL and any interested candidates, following
the process for leaderless project teams (see
:doc:`/resolutions/20141128-elections-process-for-leaderless-programs`). An
email must be sent to the ``openstack-discuss at lists.openstack.org`` mailing
list announcing the change in leadership. A patch must also be submitted to the
:repo:`openstack/governance` repository updating the project's
PTL information in ``projects.yaml``, which must be approved by the TC in order
for the appointed candidate to officially assume PTL responsibilities.

Any exception to PTL election schedule needs to be recorded in
:doc:`Election Exceptions </reference/election-exceptions>`.

In the event that there are not enough nominations to warrant voting to
happen for any project team at all, the election voting period must be skipped.
In such cases, the election officials must close the elections and publish the
results at the beginning of the planned voting period.

Voters for PTL seats ("APC")
============================

Voters for a given project's PTL election are the Active Project Contributors
("APC"), which are a subset of the Foundation Individual Members. Individual
Members who committed a change to a repository of a project over the last two
6-month release cycles are considered APC for that project team.

Candidates for PTL seats
========================

Any APC can propose their candidacy for the corresponding project PTL election.
Sitting PTLs are eligible to run for re-election each cycle, provided they
continue to meet the criteria.

Election for TC seats
=====================

The TC seats are partially renewed twice a year using staggered elections.
Members are elected for a term that expires at the conclusion of the second
scheduled election after the start of their term or after 14 months, whichever
is shorter. For this election we'll use a multiple-winner election system
see below). The election nomination as well as the voting period should be
open for at least fourteen days (2 or more weeks for each phase). The election
is held (from the nomination start date until the voting end date) no
earlier than 8 weeks and no later than 2 weeks prior to each cycle final
release date (between 'R-8' and 'R-2' week).

If required, TC and PTL elections can be held as combined election.

If a seat on the TC is vacated before the end of the term for which
the member was elected, the TC will select a replacement to serve out
the remainder of the term. The mechanism for selecting the replacement
depends on when the seat is vacated relative to the beginning of the
candidacy period for the next scheduled TC election. Selected
candidates must meet all other constraints for membership in the TC.

* If the vacancy opens less than four weeks before the candidacy
  period for the next scheduled TC election begins, and the seat
  vacated would have been contested in the upcoming election anyway,
  then the seat will remain open until the election and filled by the
  normal election process.
* If the vacancy opens less than four weeks before the candidacy
  period for the next scheduled TC election begins and the seat would
  not have been contested in the upcoming election, the candidates who
  do not win seats in the election will be consulted in the order they
  appear in the results until a candidate who is capable of serving
  agrees to serve out the partial term.
* If the vacancy opens with more than four weeks until the candidacy
  period for the next scheduled TC election begins, regardless of
  whether the vacated seat would have been contested in the next
  election, the candidates who did not win seats in the most recent
  previous TC election will be consulted in the order they appear in
  the results until a candidate who is capable of serving agrees to
  serve out the partial term.
* If there is no candidate available to fill the vacancy as per above
  mentioned criteria (either no extra candidate from election results
  or none of the candidates who do not win in previous elections accept
  the vacant TC partial term), then special election is held to fill the
  vacancy.
* Until vacant seat is filled, the current number of TC members will be
  counted as complete TC members to continue the work on motions, charter
  change etc.

Any exception to TC election schedule needs to be recorded in
:doc:`Election Exceptions </reference/election-exceptions>`

If there are not enough nominations to require an election (i.e., the number
of nominees is less than or equal to the number of available TC seats),
the election voting period must be skipped. In this case, the election
officials must close the election and publish the results at the beginning
of the planned voting period.


.. _atc:

Voters for TC seats ("AC")
==========================

The TC seats are elected by the Active Contributors ("AC"), who are
a subset of the Foundation Individual Members. Individual Members who
committed a change to a repository under the governance of the
OpenStack Technical Committee (see: :ref:`projects`,
:ref:`tc-repos` and :ref:`sig-repos`) over the
last two 6-month release cycles are automatically considered AC by their
technical contributions which are easy to mine and count. Specific
contributors who did not have a change recently accepted in one of the
OpenStack projects, but nevertheless consider themselves a contributor
to the community, can apply for AC either by sending an email to the
TC chair or by being nominated by an existing AC via email to the TC
chair. Final approval on the exception is decided by the TC itself,
and is valid one year (two elections). Examples of non-technical or
hard-to-quantify contributions include (but are not limited to):

* Bug triaging not tracked in Gerrit
* SIG membership and involvement
* Technical committee working group members
* Regular participation in code review or team feedback

We renamed the previously used term "ATC" to "AC" and the 'Active Technical
Contributors (“ATC”)' term mentioned in the Foundation bylaws is the same
as 'Active Contributors ("AC")' mentioned here.


Candidates for TC seats
=======================

Any Foundation individual member can propose their candidacy for an
available, directly-elected TC seat.

TC diversity requirement
========================

The Technical Committee in its oversight role of the OpenStack Community must
be free of bias or partiality. It must adhere to its loyalty to the OpenStack
community and strive towards its sustenance and growth.

To ensure that we remain impartial, no more than half of the TC Members shall
be Affiliated to a single organization. An individual is considered affiliated
to an organization if they are either tasked with contributing to OpenStack by
the organization or compensated for their involvement with the project,
or both.

If election or vacancy in the TC seats results in a violation of the Technical
Committee affiliation diversity requirement, the candidate with the next
highest number of votes, whose admission to the Technical Committee would not
violate the affiliation diversity requirement, will be elected as the new
Technical Committee Member instead of the member whose admission to the
Technical Committee would cause a violation of the affiliation diversity
requirement.

To this effect, candidates **MUST** declare their affiliation within their
Foundation profiles and within their election candidacies.

A violation of the diversity requirement may be temporarily waived until the
next TC election by a vote of two thirds of the TC Members. If there are not
enough candidates to meet the diversity requirement, the TC should pass a
special resolution to approve alternative solutions, such
as waiving the diversity requirement, reducing the number of TC seats, or
holding a special election.

Final determinations of affiliation in edge cases shall be made by the
Technical Committee through a formal vote, recusing any members directly
affected by the ruling. When necessary, further guidance
may be requested from the OpenInfra Foundation staff or board.

Number of seats to elect
========================

The Q3 2019 elections elected 6 seats, for a total of 13 members for the
Q3-Q4 2019 TC membership. Over 2020 the number of TC seats will be
gradually reduced to 9 members, with the following number of seats to elect:

- Q1 2020 elections: 5 seats (out of 7 incumbents): 11 members total
- Q3 2020 elections: 4 seats (out of 6 incumbents): 9 members total

Each year after 2020, the Q1 election should renew 5 seats, and the Q3 election
should renew 4 seats.

Election systems
================

For single-winner elections, a Condorcet system shall be used.

For multiple-winner elections, a Condorcet or a STV system should be used.

.. _charter-amendment-section:

Amendment
=========

Amendments to this Technical Committee charter shall be proposed in a special
motion, which needs to be approved by the affirmative vote of at least
two-thirds of the total number of TC members (rounded up: in a 13-member
committee that means a minimum of 9 approvers).

Patches with charter amendments should use the gerrit topic tag
``charter-change``.
