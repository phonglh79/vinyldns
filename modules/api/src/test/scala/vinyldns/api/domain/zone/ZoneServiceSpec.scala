/*
 * Copyright 2018 Comcast Cable Communications Management, LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package vinyldns.api.domain.zone

import org.mockito.Matchers.{any, anyString}
import org.mockito.Mockito.{doReturn, reset}
import org.scalatest._
import org.scalatest.mockito.MockitoSugar
import cats.implicits._
import vinyldns.api.Interfaces._
import vinyldns.api.domain.AccessValidations
import vinyldns.api.{GroupTestData, ResultHelpers, VinylDNSTestData}
import cats.effect._
import vinyldns.api.repository.TestDataLoader
import vinyldns.core.domain.auth.AuthPrincipal
import vinyldns.core.domain.membership._
import vinyldns.core.domain.zone._
import vinyldns.core.queue.MessageQueue

import scala.concurrent.duration._

class ZoneServiceSpec
    extends WordSpec
    with Matchers
    with MockitoSugar
    with VinylDNSTestData
    with ResultHelpers
    with BeforeAndAfterEach
    with GroupTestData
    with EitherValues {

  private val mockZoneRepo = mock[ZoneRepository]
  private val mockGroupRepo = mock[GroupRepository]
  private val mockUserRepo = mock[UserRepository]
  private val mockZoneChangeRepo = mock[ZoneChangeRepository]
  private val mockMessageQueue = mock[MessageQueue]
  private val badConnection = ZoneConnection("bad", "bad", "bad", "bad")
  private val abcZoneSummary = ZoneSummaryInfo(abcZone, abcGroup.name)
  private val xyzZoneSummary = ZoneSummaryInfo(xyzZone, xyzGroup.name)

  object TestConnectionValidator extends ZoneConnectionValidatorAlgebra {
    def validateZoneConnections(zone: Zone): Result[Unit] =
      if (zone.connection.contains(badConnection)) {
        ConnectionFailed(zone, "bad").asLeft.toResult
      } else {
        ().toResult
      }
  }

  private val underTest = new ZoneService(
    mockZoneRepo,
    mockGroupRepo,
    mockUserRepo,
    mockZoneChangeRepo,
    TestConnectionValidator,
    mockMessageQueue,
    new ZoneValidations(1000),
    AccessValidations)

  override protected def beforeEach(): Unit = {
    reset(mockGroupRepo, mockZoneRepo, mockUserRepo)
    doReturn(IO.pure(Some(grp))).when(mockGroupRepo).getGroup(anyString)
    doReturn(IO.unit).when(mockMessageQueue).send(any[ZoneChange])
  }

  "Creating Zones" should {
    "return an appropriate zone change response" in {
      doReturn(IO.pure(None)).when(mockZoneRepo).getZoneByName(anyString)

      val resultChange: ZoneChange = rightResultOf(
        underTest.connectToZone(zoneAuthorized, okAuth).map(_.asInstanceOf[ZoneChange]).value)

      resultChange.changeType shouldBe ZoneChangeType.Create
      Option(resultChange.created) shouldBe defined
      resultChange.status shouldBe ZoneChangeStatus.Pending
      resultChange.userId shouldBe okAuth.userId

      val resultZone = resultChange.zone
      Option(resultZone.id) shouldBe defined
      resultZone.email shouldBe zoneAuthorized.email
      resultZone.name shouldBe zoneAuthorized.name
      resultZone.status shouldBe ZoneStatus.Syncing
      resultZone.connection shouldBe zoneAuthorized.connection
      resultZone.shared shouldBe false
    }

    "return a ZoneAlreadyExists error if the zone exists" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZoneByName(anyString)

      val error = leftResultOf(underTest.connectToZone(zoneAuthorized, okAuth).value)

      error shouldBe a[ZoneAlreadyExistsError]
    }

    "return an InvalidZoneAdminError error if the zone admin group does not exist" in {
      doReturn(IO.pure(None)).when(mockZoneRepo).getZoneByName(anyString)
      doReturn(IO.pure(None)).when(mockGroupRepo).getGroup(anyString)

      val error = leftResultOf(underTest.connectToZone(zoneAuthorized, okAuth).value)

      error shouldBe an[InvalidZoneAdminError]
    }

    "allow the zone to be created if it exists and the zone is deleted" in {
      doReturn(IO.pure(Some(zoneDeleted))).when(mockZoneRepo).getZoneByName(anyString)

      val resultChange: ZoneChange = rightResultOf(
        underTest.connectToZone(zoneAuthorized, okAuth).map(_.asInstanceOf[ZoneChange]).value)
      resultChange.changeType shouldBe ZoneChangeType.Create
    }

    "return an error if the zone create includes a bad acl rule" in {
      val badAcl = ACLRule(baseAclRuleInfo.copy(recordMask = Some("x{5,-3}")))
      val newZone = zoneAuthorized.copy(acl = ZoneACL(Set(badAcl)))

      val error = leftResultOf(underTest.connectToZone(newZone, okAuth).value)
      error shouldBe an[InvalidRequest]
    }

    "succeed if zone is shared and user is a super user" in {
      val newZone = zoneAuthorized.copy(shared = true)
      val superAuth = okAuth.copy(signedInUser = okUser.copy(isSuper = true))
      doReturn(IO.pure(None)).when(mockZoneRepo).getZoneByName(anyString)

      val resultZone = rightResultOf(
        underTest.connectToZone(newZone, superAuth).map(_.asInstanceOf[ZoneChange]).value).zone

      Option(resultZone.id) should not be None
      resultZone.email shouldBe zoneAuthorized.email
      resultZone.name shouldBe zoneAuthorized.name
      resultZone.status shouldBe ZoneStatus.Syncing
      resultZone.connection shouldBe zoneAuthorized.connection
      resultZone.shared shouldBe true
    }

    "return a NotAuthorizedError if zone is shared and user is not a super user" in {
      val newZone = zoneAuthorized.copy(shared = true)
      doReturn(IO.pure(None)).when(mockZoneRepo).getZoneByName(anyString)

      val error = leftResultOf(underTest.connectToZone(newZone, okAuth).value)
      error shouldBe a[NotAuthorizedError]
    }
  }

  "Updating Zones" should {
    "return an update zone change response" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val doubleAuth = AuthPrincipal(TestDataLoader.okUser, Seq(grp.id, okGroup.id))
      val newZone = zoneAuthorized.copy(adminGroupId = okGroup.id)
      val resultChange: ZoneChange = rightResultOf(
        underTest.updateZone(newZone, doubleAuth).map(_.asInstanceOf[ZoneChange]).value,
        duration = 2.seconds)

      resultChange.zone.id shouldBe zoneAuthorized.id
      resultChange.changeType shouldBe ZoneChangeType.Update
      resultChange.zone.adminGroupId shouldBe newZone.adminGroupId
      resultChange.zone.adminGroupId should not be zoneAuthorized.adminGroupId
    }

    "not validate connection if unchanged" in {
      val oldZone = zoneAuthorized.copy(connection = Some(badConnection))
      doReturn(IO.pure(Some(oldZone))).when(mockZoneRepo).getZone(anyString)

      val doubleAuth = AuthPrincipal(TestDataLoader.okUser, Seq(grp.id, okGroup.id))
      val newZone = oldZone.copy(adminGroupId = okGroup.id)

      val resultChange: ZoneChange =
        rightResultOf(
          underTest.updateZone(newZone, doubleAuth).map(_.asInstanceOf[ZoneChange]).value)
      resultChange.zone.id shouldBe oldZone.id
    }

    "validate connection and fail if changed to bad" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val newZone = zoneAuthorized.copy(connection = Some(badConnection))

      val error = leftResultOf(underTest.updateZone(newZone, okAuth).value)
      error shouldBe a[ConnectionFailed]
    }

    "return an error if the user is not authorized for the zone" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val noAuth = AuthPrincipal(TestDataLoader.okUser, Seq())
      val newZone = zoneAuthorized.copy(adminGroupId = okGroup.id)

      val error = leftResultOf(underTest.updateZone(newZone, noAuth).value)
      error shouldBe a[NotAuthorizedError]
    }

    "return an error if the zone update adds a bad acl rule" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val badAcl = ACLRule(baseAclRuleInfo.copy(recordMask = Some("x{5,-3}")))
      val newZone = zoneAuthorized.copy(acl = ZoneACL(Set(badAcl)))

      val error = leftResultOf(underTest.updateZone(newZone, okAuth).value)
      error shouldBe an[InvalidRequest]
    }
  }

  "Deleting Zones" should {
    "return an delete zone change response" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val resultChange: ZoneChange = rightResultOf(
        underTest.deleteZone(zoneAuthorized.id, okAuth).map(_.asInstanceOf[ZoneChange]).value)

      resultChange.zone.id shouldBe zoneAuthorized.id
      resultChange.changeType shouldBe ZoneChangeType.Delete
    }

    "return an error if the user is not authorized for the zone" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val noAuth = AuthPrincipal(TestDataLoader.okUser, Seq())

      val error = leftResultOf(underTest.deleteZone(zoneAuthorized.id, noAuth).value)
      error shouldBe a[NotAuthorizedError]
    }
  }

  "Syncing a zone" should {
    "return a sync zone response" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val resultChange: ZoneChange = rightResultOf(
        underTest.syncZone(zoneAuthorized.id, okAuth).map(_.asInstanceOf[ZoneChange]).value)

      resultChange.zone.id shouldBe zoneAuthorized.id
      resultChange.changeType shouldBe ZoneChangeType.Sync
      resultChange.status shouldBe ZoneChangeStatus.Pending
    }

    "return an error if the user is not authorized for the zone" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val noAuth = AuthPrincipal(TestDataLoader.okUser, Seq())

      val error = leftResultOf(underTest.syncZone(zoneAuthorized.id, noAuth).value)
      error shouldBe a[NotAuthorizedError]
    }
  }

  "Getting a Zone" should {
    "not fail with no zone returned" in {
      doReturn(IO.pure(None)).when(mockZoneRepo).getZone("notAZoneId")

      val error = leftResultOf(underTest.getZone("notAZoneId", okAuth).value)
      error shouldBe a[ZoneNotFoundError]
    }

    "return an error if the user is not authorized for the zone" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val noAuth = AuthPrincipal(TestDataLoader.okUser, Seq())

      val error = leftResultOf(underTest.getZone(zoneAuthorized.id, noAuth).value)
      error shouldBe a[NotAuthorizedError]
    }

    "return the appropriate zone as a ZoneInfo" in {
      doReturn(IO.pure(Some(abcZone))).when(mockZoneRepo).getZone(abcZone.id)
      doReturn(IO.pure(ListUsersResults(Seq(), None)))
        .when(mockUserRepo)
        .getUsers(any[Set[String]], any[Option[String]], any[Option[Int]])
      doReturn(IO.pure(Set(abcGroup))).when(mockGroupRepo).getGroups(any[Set[String]])
      doReturn(IO.pure(Some(abcGroup))).when(mockGroupRepo).getGroup(anyString)

      val expectedZoneInfo = ZoneInfo(abcZone, ZoneACLInfo(Set()), abcGroup.name)
      val result = underTest.getZone(abcZone.id, abcAuth).value.unsafeRunSync()
      result.right.value shouldBe expectedZoneInfo
    }

    "filter out ACL rules that have no matching group or user" in {
      val goodUser = User("goodUser", "access", "secret")
      val goodGroup = Group("goodGroup", "email")

      val goodUserRule = baseAclRule.copy(userId = Some(goodUser.id), groupId = None)
      val badUserRule = goodUserRule.copy(userId = Some("bad"))
      val goodGroupRule = baseAclRule.copy(userId = None, groupId = Some(goodGroup.id))
      val badGroupRule = goodGroupRule.copy(groupId = Some("bad"))
      val goodAllRule = baseAclRule.copy(userId = None, groupId = None)

      val goodUserRuleInfo = ACLRuleInfo(goodUserRule, Some("goodUser"))
      val goodGroupRuleInfo = ACLRuleInfo(goodGroupRule, Some("goodGroup"))
      val goodAllRuleInfo = ACLRuleInfo(goodAllRule, Some("All Users"))

      val acl = ZoneACL(Set(goodUserRule, badUserRule, goodGroupRule, badGroupRule, goodAllRule))
      val zoneWithRules = abcZone.copy(acl = acl)

      doReturn(IO.pure(Some(zoneWithRules))).when(mockZoneRepo).getZone(zoneWithRules.id)
      doReturn(IO.pure(ListUsersResults(Seq(goodUser), None)))
        .when(mockUserRepo)
        .getUsers(any[Set[String]], any[Option[String]], any[Option[Int]])
      doReturn(IO.pure(Set(goodGroup))).when(mockGroupRepo).getGroups(any[Set[String]])
      doReturn(IO.pure(Some(goodGroup))).when(mockGroupRepo).getGroup(anyString)

      val expectedZoneInfo = ZoneInfo(
        zoneWithRules,
        ZoneACLInfo(Set(goodUserRuleInfo, goodGroupRuleInfo, goodAllRuleInfo)),
        goodGroup.name)
      val result: ZoneInfo = rightResultOf(underTest.getZone(zoneWithRules.id, abcAuth).value)
      result shouldBe expectedZoneInfo
    }

    "return Unknown group name if zone admin group cannot be found" in {
      doReturn(IO.pure(Some(abcZone))).when(mockZoneRepo).getZone(abcZone.id)
      doReturn(IO.pure(ListUsersResults(Seq(), None)))
        .when(mockUserRepo)
        .getUsers(any[Set[String]], any[Option[String]], any[Option[Int]])
      doReturn(IO.pure(Set(abcGroup))).when(mockGroupRepo).getGroups(any[Set[String]])
      doReturn(IO.pure(None)).when(mockGroupRepo).getGroup(anyString)

      val expectedZoneInfo = ZoneInfo(abcZone, ZoneACLInfo(Set()), "Unknown group name")
      val result: ZoneInfo = rightResultOf(underTest.getZone(abcZone.id, abcAuth).value)
      result shouldBe expectedZoneInfo
    }
  }

  "ListZones" should {
    "not fail with no zones returned" in {
      doReturn(IO.pure(List())).when(mockZoneRepo).listZones(abcAuth, None, None, 100)
      doReturn(IO.pure(Set(abcGroup))).when(mockGroupRepo).getGroups(any[Set[String]])

      val result: ListZonesResponse = rightResultOf(underTest.listZones(abcAuth).value)
      result.zones shouldBe List()
      result.maxItems shouldBe 100
      result.startFrom shouldBe None
      result.nameFilter shouldBe None
      result.nextId shouldBe None
    }

    "return the appropriate zones" in {
      doReturn(IO.pure(List(abcZone, xyzZone)))
        .when(mockZoneRepo)
        .listZones(abcAuth, None, None, 100)
      doReturn(IO.pure(Set(abcGroup, xyzGroup)))
        .when(mockGroupRepo)
        .getGroups(any[Set[String]])

      val result: ListZonesResponse = rightResultOf(underTest.listZones(abcAuth).value)
      result.zones shouldBe List(abcZoneSummary, xyzZoneSummary)
      result.maxItems shouldBe 100
      result.startFrom shouldBe None
      result.nameFilter shouldBe None
      result.nextId shouldBe None
    }

    "return Unknown group name if zone admin group cannot be found" in {
      doReturn(IO.pure(List(abcZone, xyzZone)))
        .when(mockZoneRepo)
        .listZones(abcAuth, None, None, 100)
      doReturn(IO.pure(Set(okGroup))).when(mockGroupRepo).getGroups(any[Set[String]])

      val result: ListZonesResponse = rightResultOf(underTest.listZones(abcAuth).value)
      val expectedZones =
        List(abcZoneSummary, xyzZoneSummary).map(_.copy(adminGroupName = "Unknown group name"))
      result.zones shouldBe expectedZones
      result.maxItems shouldBe 100
      result.startFrom shouldBe None
      result.nameFilter shouldBe None
      result.nextId shouldBe None
    }

    "set the nextId appropriately" in {
      doReturn(IO.pure(List(abcZone, xyzZone)))
        .when(mockZoneRepo)
        .listZones(abcAuth, None, None, 2)
      doReturn(IO.pure(Set(abcGroup, xyzGroup)))
        .when(mockGroupRepo)
        .getGroups(any[Set[String]])

      val result: ListZonesResponse =
        rightResultOf(underTest.listZones(abcAuth, maxItems = 2).value)
      result.zones shouldBe List(abcZoneSummary, xyzZoneSummary)
      result.maxItems shouldBe 2
      result.startFrom shouldBe None
      result.nameFilter shouldBe None
      result.nextId shouldBe Some(2)
    }

    "set the nameFilter when provided" in {
      doReturn(IO.pure(List(abcZone, xyzZone)))
        .when(mockZoneRepo)
        .listZones(abcAuth, Some("foo"), None, 2)
      doReturn(IO.pure(Set(abcGroup, xyzGroup)))
        .when(mockGroupRepo)
        .getGroups(any[Set[String]])

      val result: ListZonesResponse =
        rightResultOf(underTest.listZones(abcAuth, nameFilter = Some("foo"), maxItems = 2).value)
      result.zones shouldBe List(abcZoneSummary, xyzZoneSummary)
      result.nameFilter shouldBe Some("foo")
      result.nextId shouldBe Some(2)
      result.maxItems shouldBe 2
    }

    "set the startFrom when provided" in {
      doReturn(IO.pure(List(abcZone, xyzZone)))
        .when(mockZoneRepo)
        .listZones(abcAuth, None, Some(4), 2)
      doReturn(IO.pure(Set(abcGroup, xyzGroup)))
        .when(mockGroupRepo)
        .getGroups(any[Set[String]])

      val result: ListZonesResponse =
        rightResultOf(underTest.listZones(abcAuth, startFrom = Some(4), maxItems = 2).value)
      result.zones shouldBe List(abcZoneSummary, xyzZoneSummary)
      result.startFrom shouldBe Some(4)
    }

    "set the nextId to be the current result set size plus the start from" in {
      doReturn(IO.pure(List(abcZone, xyzZone)))
        .when(mockZoneRepo)
        .listZones(abcAuth, None, Some(4), 2)
      doReturn(IO.pure(Set(abcGroup, xyzGroup)))
        .when(mockGroupRepo)
        .getGroups(any[Set[String]])

      val result: ListZonesResponse =
        rightResultOf(underTest.listZones(abcAuth, startFrom = Some(4), maxItems = 2).value)
      result.zones shouldBe List(abcZoneSummary, xyzZoneSummary)
      result.nextId shouldBe Some(6)
    }
  }

  "listZoneChanges" should {
    "retrieve the zone changes" in {
      doReturn(IO.pure(Some(zoneAuthorized)))
        .when(mockZoneRepo)
        .getZone(zoneAuthorized.id)
      doReturn(IO.pure(ListZoneChangesResults(List(zoneUpdate, zoneCreate))))
        .when(mockZoneChangeRepo)
        .listZoneChanges(zoneAuthorized.id, startFrom = None, maxItems = 100)

      val result: ListZoneChangesResponse =
        rightResultOf(underTest.listZoneChanges(zoneAuthorized.id, okAuth).value)

      result.zoneChanges shouldBe List(zoneUpdate, zoneCreate)
      result.zoneId shouldBe zoneActive.id
    }

    "return a zone with no changes if no changes exist" in {
      doReturn(IO.pure(Some(zoneAuthorized)))
        .when(mockZoneRepo)
        .getZone(zoneAuthorized.id)
      doReturn(IO.pure(ListZoneChangesResults(items = Nil)))
        .when(mockZoneChangeRepo)
        .listZoneChanges(zoneAuthorized.id, startFrom = None, maxItems = 100)

      val result: ListZoneChangesResponse =
        rightResultOf(underTest.listZoneChanges(zoneAuthorized.id, okAuth).value)

      result.zoneChanges shouldBe empty
      result.zoneId shouldBe zoneAuthorized.id
    }

    "return a NotAuthorizedError" in {
      doReturn(IO.pure(Some(zoneNotAuthorized)))
        .when(mockZoneRepo)
        .getZone(zoneNotAuthorized.id)

      val error = leftResultOf(underTest.listZoneChanges(zoneNotAuthorized.id, okAuth).value)
      error shouldBe a[NotAuthorizedError]
    }

    "return the zone changes sorted by created date desc" in {
      // zone change 2 is later than zone change 1 and should come first
      doReturn(IO.pure(Some(zoneAuthorized)))
        .when(mockZoneRepo)
        .getZone(zoneAuthorized.id)

      doReturn(IO.pure(ListZoneChangesResults(List(zoneUpdate, zoneCreate))))
        .when(mockZoneChangeRepo)
        .listZoneChanges(zoneId = zoneAuthorized.id, startFrom = None, maxItems = 100)

      val result: ListZoneChangesResponse =
        rightResultOf(underTest.listZoneChanges(zoneAuthorized.id, okAuth).value)

      result.zoneChanges.head shouldBe zoneUpdate
      result.zoneChanges(1) shouldBe zoneCreate
    }
  }

  "AddAclRule" should {
    "fail if the user is not authorized for the zone" in {
      doReturn(IO.pure(Some(notAuthorizedZone))).when(mockZoneRepo).getZone(anyString)

      val error =
        leftResultOf(underTest.addACLRule(notAuthorizedZone.id, userAclRuleInfo, okAuth).value)
      error shouldBe a[NotAuthorizedError]
    }

    "generate a zone update if the request is valid" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val result: ZoneChange = rightResultOf(
        underTest
          .addACLRule(zoneAuthorized.id, userAclRuleInfo, okAuth)
          .map(_.asInstanceOf[ZoneChange])
          .value)

      result.changeType shouldBe ZoneChangeType.Update
      result.zone.acl.rules.size shouldBe 1
      result.zone.acl.rules should contain(userAclRule)
    }

    "fail if mask is an invalid regex" in {
      doReturn(IO.pure(Some(zoneAuthorized))).when(mockZoneRepo).getZone(anyString)

      val invalidRegexMaskRuleInfo = baseAclRuleInfo.copy(recordMask = Some("x{5,-3}"))
      val error =
        leftResultOf(
          underTest.addACLRule(zoneAuthorized.id, invalidRegexMaskRuleInfo, okAuth).value)
      error shouldBe an[InvalidRequest]
    }
  }

  "DeleteAclRule" should {
    "fail if the user is not authorized for the zone" in {
      doReturn(IO.pure(Some(notAuthorizedZone))).when(mockZoneRepo).getZone(anyString)

      val error =
        leftResultOf(underTest.deleteACLRule(notAuthorizedZone.id, userAclRuleInfo, okAuth).value)
      error shouldBe a[NotAuthorizedError]
    }

    "generate a zone update if the request is valid" in {
      val acl = ZoneACL(Set(userAclRule))
      val zone = zoneAuthorized.copy(acl = acl)
      doReturn(IO.pure(Some(zone))).when(mockZoneRepo).getZone(anyString)

      val result: ZoneChange = rightResultOf(
        underTest
          .deleteACLRule(zone.id, userAclRuleInfo, okAuth)
          .map(_.asInstanceOf[ZoneChange])
          .value)

      result.changeType shouldBe ZoneChangeType.Update
      result.zone.acl.rules.size shouldBe 0
    }
  }
}
